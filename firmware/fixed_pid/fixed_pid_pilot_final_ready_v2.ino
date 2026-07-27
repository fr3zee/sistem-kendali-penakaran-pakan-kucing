/**
 * FIXED PID v8 - PET FEEDER
 * ===========================
 * Perubahan dari v7:
 *   1. PID PENUH (P+I+D aktif) — sesuai revisi dosen penguji
 *   2. Parameter awal dari Z-N baseline (rata-rata Zona 2)
 *   3. Early stop 0.4g
 *   4. Pembatasan akumulasi integral disesuaikan dengan Ki
 *   5. Anti-bridging dua lapis (shake preventif + hammer reaktif)
 *
 * PERBANDINGAN ADIL vs GAIN SCHEDULING:
 *   - Sudut range sama   : 20°-40°
 *   - Early stop sama    : 0.4g
 *   - Anti-bridging sama : dua lapis (shake + hammer)
 *   - Sampling sama      : ~260ms aktual
 *   - Satu-satunya beda  : gain tetap vs gain per zona
 *
 * TUNING VIA SERIAL:
 *   Langkah 1: p<val> (mulai P saja, Ki=0, Kd=0)
 *   Langkah 2: i<val> (tambah I untuk hilangkan SSE)
 *   Langkah 3: d<val> (tambah D untuk redam overshoot)
 *
 * REFERENSI:
 *   [5]  Ding et al. (2026) - stokastik granular
 *   [6]  Schulze (2021) - bulk solid flow
 *   [10] Zhang et al. (2025) - kriteria akurasi dispensing
 *   [13] Åström & Wittenmark (2008) - PID tuning
 */

#include <ESP32Servo.h>
#include <HX711.h>

// ============================================================
// PIN
// ============================================================
#define SERVO_PIN      13
#define LOADCELL_DOUT   4
#define LOADCELL_SCK    2

// ============================================================
// KALIBRASI
// ============================================================
const float FAKTOR_KALIBRASI = 901.0;

// ============================================================
// PARAMETER SERVO — SAMA dengan Gain Scheduling v3
// ============================================================
const int SUDUT_TUTUP = 0;
const int SUDUT_MIN   = 20;   // DISERAGAMKAN dengan GS v3
const int SUDUT_BUKA  = 40;   // DISERAGAMKAN dengan GS v3

// ============================================================
// PARAMETER SISTEM — SAMA dengan Gain Scheduling v3
// ============================================================
const int           INTERVAL_KONTROL  = 100;    // ms
const int           SHAKE_INTERVAL_MS = 2000;   // ms
const int           SHAKE_AMPLITUDO   = 10;      // derajat — DISERAGAMKAN
const int           SHAKE_DURASI_MS   = 300;    // ms
const unsigned long TIMEOUT_MS        = 120000; // ms — batas observasi/safety disamakan

// Anti-bridging — SAMA dengan GS v3
const float         BRIDGING_DELTA_MIN = 0.5;
const unsigned long BRIDGING_WINDOW_MS = 3000;
const unsigned long BRIDGING_PULSE_MS  = 2000;
const float         HAMMER_THRESHOLD_G  = 3.0;

// ============================================================
// PARAMETER PID — FINAL (hasil tuning iteratif 30+ trial)
// Baseline awal dari Z-N sudut 30° (Kp=1.37, Ki=1.33, Kd=0.35)
// lalu disesuaikan melalui tuning langsung pada hardware.
// ============================================================
float Kp = 2.50;   // final — tuning iteratif
float Ki = 0.15;   // final — tuning iteratif
float Kd = 0.03;   // final — tuning iteratif
float INTEGRAL_MAX = 30.0;  // pembatasan akumulasi integral

// ============================================================
// EARLY STOP
// ============================================================
float EARLY_STOP_MARGIN = 0.4;  // gram — final fair comparison dengan GS PID

// ============================================================
// METRIK RESPONSE UNTUK ANALISIS
// ============================================================
const float RISE_LOW_PCT       = 10.0;  // t10 untuk rise time 10-90%
const float RISE_HIGH_PCT      = 90.0;  // t90 untuk rise time 10-90%
const float SETTLING_TOL_PCT   = 5.0;   // band settling ±5% dari setpoint

// ============================================================
// SETPOINT
// ============================================================
float setpoint = 20.0;

// ============================================================
// VARIABEL KONTROL
// ============================================================
float  massaAktual     = 0.0;
float  errorAktual     = 0.0;
float  integralVal     = 0.0;
float  errorSebelumnya = 0.0;
float  outputPID       = 0.0;
int    sudutAktif      = 0;

bool          sedangDispensing  = false;
unsigned long tKontrolTerakhir  = 0;
unsigned long tShakeTerakhir    = 0;
unsigned long tMulaiDispensing  = 0;
bool          shakeAktif        = false;
unsigned long tShakeMulai       = 0;
int           nPercobaan        = 0;

// Anti-bridging
float         massaSaatCekBridging = 0.0;
unsigned long tCekBridging         = 0;
bool          bridgingPulseAktif   = false;
unsigned long tBridgingPulseMulai  = 0;
int           nBridgingDeteksi     = 0;

// Metrik response
bool          rise10Reached          = false;
bool          rise90Reached          = false;
bool          firstToleranceReached  = false;
bool          settlingCandidateActive= false;
unsigned long tRise10Ms              = 0;
unsigned long tRise90Ms              = 0;
unsigned long tFirstToleranceMs      = 0;
unsigned long tSettlingCandidateMs   = 0;
float         maxMassDuringTrial     = 0.0;

Servo  myServo;
HX711  scale;

// ============================================================
// SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  myServo.attach(SERVO_PIN);
  myServo.write(SUDUT_TUTUP);
  scale.begin(LOADCELL_DOUT, LOADCELL_SCK);
  scale.set_scale(FAKTOR_KALIBRASI);
  scale.tare(10);
  tampilHeader();
}

// ============================================================
// LOOP
// ============================================================
void loop() {
  bacaSerial();
  if (!sedangDispensing) return;

  unsigned long sekarang = millis();

  if (sekarang - tMulaiDispensing > TIMEOUT_MS) {
    stopDispensing("TIMEOUT");
    return;
  }

  if (sekarang - tKontrolTerakhir >= INTERVAL_KONTROL) {
    tKontrolTerakhir = sekarang;

    massaAktual = scale.get_units(3);
    if (massaAktual < 0) massaAktual = 0;

    errorAktual = setpoint - massaAktual;

    updateResponseMetrics(sekarang);

    // Early stop — SAMA dengan GS v3 [5][6]
    if (massaAktual >= (setpoint - EARLY_STOP_MARGIN)) {
      stopDispensing("TARGET");
      return;
    }

    // Anti-bridging — SAMA dengan GS v3 [5][6]
    if (sekarang - tCekBridging >= BRIDGING_WINDOW_MS) {
      if ((massaAktual - massaSaatCekBridging) < BRIDGING_DELTA_MIN
          && errorAktual > HAMMER_THRESHOLD_G) {  // tidak hammer dekat target
        nBridgingDeteksi++;
        bridgingPulseAktif  = true;
        tBridgingPulseMulai = sekarang;
        myServo.write(SUDUT_TUTUP);
        Serial.print("BRIDGING #"); Serial.print(nBridgingDeteksi);
        Serial.print(" @"); Serial.print(massaAktual, 2);
        Serial.println("g hammer");
      }
      massaSaatCekBridging = massaAktual;
      tCekBridging         = sekarang;
    }
    if (bridgingPulseAktif) {
      unsigned long elapsed = sekarang - tBridgingPulseMulai;
      if (elapsed < 300) {
        myServo.write(SUDUT_TUTUP);       // fase tutup dulu
      } else if (elapsed < 300 + BRIDGING_PULSE_MS) {
        myServo.write(SUDUT_BUKA);        // fase buka penuh
      } else {
        bridgingPulseAktif = false;
        myServo.write(sudutAktif);        // kembali ke sudut PID
      }
    }

    // Hitung PID diskrit — MURNI, tanpa bang-bang [13][22]
    // Fixed PID: parameter konstan di seluruh range operasi
    float dt = INTERVAL_KONTROL / 1000.0;

    // Integral — dengan pembatasan akumulasi
    integralVal += errorAktual * dt;
    integralVal  = constrain(integralVal, 0, INTEGRAL_MAX);

    // Derivatif
    float derivatif = (errorAktual - errorSebelumnya) / dt;
    errorSebelumnya = errorAktual;

    outputPID = (Kp * errorAktual) + (Ki * integralVal) + (Kd * derivatif);
    outputPID = constrain(outputPID, 0, 100);

    // Mapping output → sudut — SAMA dengan GS v3
    // Tidak ada bang-bang — PID murni mengontrol sudut
    int sudutTarget;
    if (outputPID < 1) {
      sudutTarget = SUDUT_TUTUP;
    } else {
      sudutTarget = map((int)outputPID, 1, 100, SUDUT_MIN, SUDUT_BUKA);
    }
    sudutAktif = sudutTarget;
    if (!shakeAktif && !bridgingPulseAktif) myServo.write(sudutTarget);

    // Log — format SAMA dengan GS v3 + kolom eNorm untuk analisis zona
    float eNorm = (errorAktual / setpoint) * 100.0;
    Serial.print("DATA,");
    Serial.print(sekarang - tMulaiDispensing);
    Serial.print(","); Serial.print(massaAktual, 2);
    Serial.print(","); Serial.print(errorAktual, 2);
    Serial.print(","); Serial.print(eNorm, 1);
    Serial.print(","); Serial.print(outputPID, 1);
    Serial.print(","); Serial.print(sudutTarget);
    // Tambah kolom zona ekuivalen untuk analisis — bukan untuk kontrol
    String zonaEkuivalen;
    if (eNorm > 50.0)       zonaEkuivalen = "Z1";
    else if (eNorm > 15.0)  zonaEkuivalen = "Z2";
    else                    zonaEkuivalen = "Z3";
    Serial.print(","); Serial.print(zonaEkuivalen);
    Serial.print(","); Serial.print(integralVal, 3);
    Serial.print(","); Serial.print(derivatif, 3);
    Serial.print(","); Serial.println(nBridgingDeteksi);
  }

  prosesShake(sekarang);
}

// ============================================================
// UPDATE METRIK RESPONSE
// ============================================================
void updateResponseMetrics(unsigned long sekarang) {
  unsigned long elapsed = sekarang - tMulaiDispensing;

  if (massaAktual > maxMassDuringTrial) maxMassDuringTrial = massaAktual;

  if (!rise10Reached && massaAktual >= (RISE_LOW_PCT / 100.0) * setpoint) {
    rise10Reached = true;
    tRise10Ms = elapsed;
  }

  if (!rise90Reached && massaAktual >= (RISE_HIGH_PCT / 100.0) * setpoint) {
    rise90Reached = true;
    tRise90Ms = elapsed;
  }

  float settlingTolG = setpoint * (SETTLING_TOL_PCT / 100.0);
  bool inBand = abs(setpoint - massaAktual) <= settlingTolG;

  if (inBand) {
    if (!firstToleranceReached) {
      firstToleranceReached = true;
      tFirstToleranceMs = elapsed;
    }
    if (!settlingCandidateActive) {
      settlingCandidateActive = true;
      tSettlingCandidateMs = elapsed;
    }
  } else {
    settlingCandidateActive = false;
    tSettlingCandidateMs = 0;
  }
}

// ============================================================
// PROSES SHAKE — SAMA dengan GS v3
// ============================================================
void prosesShake(unsigned long sekarang) {
  if (!shakeAktif &&
      sekarang - tShakeTerakhir >= (unsigned long)SHAKE_INTERVAL_MS) {
    shakeAktif     = true;
    tShakeMulai    = sekarang;
    tShakeTerakhir = sekarang;
    if (!bridgingPulseAktif)
      myServo.write(constrain(sudutAktif + SHAKE_AMPLITUDO, SUDUT_MIN, SUDUT_BUKA + 5));
  } else if (shakeAktif &&
             sekarang - tShakeMulai >= (unsigned long)SHAKE_DURASI_MS) {
    shakeAktif = false;
    if (!bridgingPulseAktif) myServo.write(sudutAktif);
  } else if (shakeAktif &&
             sekarang - tShakeMulai >= (unsigned long)(SHAKE_DURASI_MS / 2)) {
    if (!bridgingPulseAktif) myServo.write(sudutAktif);
  }
}

// ============================================================
// MULAI DISPENSING
// ============================================================
void mulaiDispensing() {
  scale.tare(10);
  delay(300);

  nPercobaan++;
  massaAktual          = 0;
  integralVal          = 0;
  errorSebelumnya      = 0;
  outputPID            = 0;
  sudutAktif           = SUDUT_TUTUP;
  sedangDispensing     = true;
  tKontrolTerakhir     = millis();
  tShakeTerakhir       = millis();
  tMulaiDispensing     = millis();
  massaSaatCekBridging = 0.0;
  tCekBridging         = millis();
  bridgingPulseAktif   = false;
  nBridgingDeteksi     = 0;

  rise10Reached = false;
  rise90Reached = false;
  firstToleranceReached = false;
  settlingCandidateActive = false;
  tRise10Ms = 0;
  tRise90Ms = 0;
  tFirstToleranceMs = 0;
  tSettlingCandidateMs = 0;
  maxMassDuringTrial = 0.0;

  Serial.println("=== TRIAL START ===");
  Serial.print("Controller: "); Serial.println("Fixed PID");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);
  Serial.print("Kp: "); Serial.println(Kp, 3);
  Serial.print("Ki: "); Serial.println(Ki, 3);
  Serial.print("Kd: "); Serial.println(Kd, 3);
  Serial.print("IntMax: "); Serial.println(INTEGRAL_MAX, 2);
  Serial.print("ServoMin_deg: "); Serial.println(SUDUT_MIN);
  Serial.print("ServoMax_deg: "); Serial.println(SUDUT_BUKA);
  Serial.print("HammerThreshold_g: "); Serial.println(HAMMER_THRESHOLD_G, 2);
  Serial.print("Sampling_ms: "); Serial.println(INTERVAL_KONTROL);
  Serial.println("DataFormat: DATA,ms,mass_g,error_g,error_pct,output,servo_deg,zone,I,D,bridging_count");
  Serial.println("=== DATA START ===");
}

// ============================================================
// STOP DISPENSING
// ============================================================
void stopDispensing(String alasan) {
  sedangDispensing = false;
  myServo.write(SUDUT_TUTUP);
  shakeAktif  = false;
  integralVal = 0;

  delay(500);
  float massaFinal  = scale.get_units(10);
  if (massaFinal < 0) massaFinal = 0;
  float errorAkhir  = massaFinal - setpoint;
  float errorPersen = (errorAkhir / setpoint) * 100.0;
  unsigned long durasi = millis() - tMulaiDispensing;

  if (massaFinal > maxMassDuringTrial) maxMassDuringTrial = massaFinal;
  float settlingTolG = setpoint * (SETTLING_TOL_PCT / 100.0);
  bool finalInSettlingBand = abs(errorAkhir) <= settlingTolG;
  long timeTo90Ms = rise90Reached ? (long)tRise90Ms : -1;
  long riseTime10_90Ms = (rise10Reached && rise90Reached) ? (long)(tRise90Ms - tRise10Ms) : -1;
  long timeToToleranceMs = firstToleranceReached ? (long)tFirstToleranceMs : -1;
  long settlingTimeMs = -1;
  if (finalInSettlingBand) {
    if (settlingCandidateActive) settlingTimeMs = (long)tSettlingCandidateMs;
    else if (firstToleranceReached) settlingTimeMs = (long)tFirstToleranceMs;
    else settlingTimeMs = (long)durasi;  // perkiraan jika masuk band setelah servo ditutup
  }
  float maxOvershootG = max(0.0f, maxMassDuringTrial - setpoint);
  float maxOvershootPct = (maxOvershootG / setpoint) * 100.0;

  Serial.println("--------------------------------------------");
  Serial.print("STOP       : "); Serial.println(alasan);
  Serial.print("Setpoint   : "); Serial.print(setpoint, 1); Serial.println("g");
  Serial.print("Massa akhir: "); Serial.print(massaFinal, 2); Serial.println("g");
  Serial.print("Error akhir: "); Serial.print(errorAkhir, 2); Serial.println("g");
  Serial.print("Error%     : "); Serial.print(errorPersen, 1); Serial.println("%");
  Serial.print("Durasi     : "); Serial.print(durasi); Serial.println("ms");
  Serial.print("Bridging   : "); Serial.print(nBridgingDeteksi); Serial.println("x");

  String statusAkhir;
  if      (abs(errorPersen) <= 5.0) statusAkhir = "AKURAT";
  else if (errorAkhir > 0)          statusAkhir = "OVERSHOOT";
  else                              statusAkhir = "UNDERSHOOT";

  Serial.print("STATUS     : "); Serial.println(statusAkhir);

  Serial.println("=== SUMMARY TRIAL ===");
  Serial.print("Controller: "); Serial.println("Fixed PID");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);
  Serial.print("Kp: "); Serial.println(Kp, 3);
  Serial.print("Ki: "); Serial.println(Ki, 3);
  Serial.print("Kd: "); Serial.println(Kd, 3);
  Serial.print("IntMax: "); Serial.println(INTEGRAL_MAX, 2);
  Serial.print("ServoMin_deg: "); Serial.println(SUDUT_MIN);
  Serial.print("ServoMax_deg: "); Serial.println(SUDUT_BUKA);
  Serial.print("HammerThreshold_g: "); Serial.println(HAMMER_THRESHOLD_G, 2);
  Serial.print("FinalMass_g: "); Serial.println(massaFinal, 2);
  Serial.print("FinalError_g: "); Serial.println(errorAkhir, 2);
  Serial.print("FinalError_pct: "); Serial.println(errorPersen, 2);
  Serial.print("Duration_ms: "); Serial.println(durasi);
  Serial.print("Duration_s: "); Serial.println(durasi / 1000.0, 2);
  Serial.print("TimeTo90_ms: "); Serial.println(timeTo90Ms);
  Serial.print("RiseTime_10_90_ms: "); Serial.println(riseTime10_90Ms);
  Serial.print("TimeToTolerance_ms: "); Serial.println(timeToToleranceMs);
  Serial.print("SettlingTime_ms: "); Serial.println(settlingTimeMs);
  Serial.print("SettlingTol_pct: "); Serial.println(SETTLING_TOL_PCT, 2);
  Serial.print("SettlingTol_g: "); Serial.println(settlingTolG, 2);
  Serial.print("MaxMass_g: "); Serial.println(maxMassDuringTrial, 2);
  Serial.print("MaxOvershoot_g: "); Serial.println(maxOvershootG, 2);
  Serial.print("MaxOvershoot_pct: "); Serial.println(maxOvershootPct, 2);
  Serial.print("BridgingCount: "); Serial.println(nBridgingDeteksi);
  Serial.print("Status: "); Serial.println(statusAkhir);
  Serial.println("Valid: TRUE");
  Serial.print("StopReason: "); Serial.println(alasan);
  Serial.println("=== TRIAL END ===");

  Serial.println("--------------------------------------------");
  Serial.println("r=reset | g=ulangi | c=parameter");
}

// ============================================================
// BACA SERIAL
// ============================================================
void bacaSerial() {
  if (!Serial.available()) return;
  String input = Serial.readStringUntil('\n');
  input.trim();
  if (input.length() < 1) return;

  char  cmd = input.charAt(0);
  float val = input.substring(1).toFloat();

  switch (cmd) {
    case 'p': case 'P':
      Kp = val;
      Serial.print("Kp = "); Serial.println(Kp, 2); break;

    case 'i': case 'I':
      Ki = val;
      Serial.print("Ki = "); Serial.println(Ki, 3);
      break;

    case 'd': case 'D':
      Kd = val;
      Serial.print("Kd = "); Serial.println(Kd, 3);
      break;

    case 's': case 'S':
      setpoint = val;
      Serial.print("Setpoint = "); Serial.print(setpoint, 1); Serial.println("g"); break;

    case 'e': case 'E':
      EARLY_STOP_MARGIN = val;
      Serial.print("Early stop = SP - "); Serial.print(EARLY_STOP_MARGIN); Serial.println("g"); break;

    case 'g': case 'G':
      if (!sedangDispensing) mulaiDispensing(); break;

    case 'r': case 'R':
      sedangDispensing = false;
      myServo.write(SUDUT_TUTUP);
      integralVal = 0;
      delay(300);
      scale.tare(10);
      Serial.println("RESET. Servo tutup. Tare selesai. Siap."); break;

    case 'x': case 'X':
      stopDispensing("MANUAL"); break;

    case 'c': case 'C':
      cetakParameter(); break;

    case 't': case 'T': {
      int nextTrial = (int)val;
      if (nextTrial < 1) {
        Serial.println("ERROR: Trial berikutnya minimal 1");
        break;
      }
      nPercobaan = nextTrial - 1;
      Serial.print("Trial berikutnya diset ke: ");
      Serial.println(nextTrial);
      break;
    }

    default:
      Serial.println("CMD: p/i/d/s/e/g/t/r/x/c");
  }
}

// ============================================================
// CETAK PARAMETER
// ============================================================
void cetakParameter() {
  Serial.println("======== PARAMETER AKTIF (Fixed PID) ========");
  Serial.print("Setpoint   : "); Serial.print(setpoint, 1); Serial.println("g");
  Serial.print("Kp         : "); Serial.println(Kp, 2);
  Serial.print("Ki         : "); Serial.println(Ki, 3);
  Serial.print("Kd         : "); Serial.println(Kd, 3);
  Serial.print("IntMax     : "); Serial.println(INTEGRAL_MAX, 1);
  Serial.print("SUDUT_MIN  : "); Serial.print(SUDUT_MIN); Serial.println("deg");
  Serial.print("SUDUT_BUKA : "); Serial.print(SUDUT_BUKA); Serial.println("deg");
  Serial.print("EARLY_STOP : SP - "); Serial.print(EARLY_STOP_MARGIN); Serial.println("g");
  Serial.print("STOP saat  : "); Serial.print(setpoint - EARLY_STOP_MARGIN, 1); Serial.println("g");
  Serial.print("HAMMER_TH  : error > "); Serial.print(HAMMER_THRESHOLD_G, 1); Serial.println("g");
  Serial.println("=================================================");
}

void tampilHeader() {
  Serial.println("=========================================");
  Serial.println("   FIXED PID v8 - PET FEEDER - ESP32");
  Serial.println("=========================================");
  Serial.println("PID penuh (P+I+D) - Z-N baseline");
  Serial.println("Sudut: 20-40deg | ES: 0.4g");
  Serial.println("Anti-bridging: shake + hammer");
  Serial.println("-----------------------------------------");
  Serial.println("PERINTAH:");
  Serial.println("  p<val> = Kp    i<val> = Ki    d<val> = Kd");
  Serial.println("  s<val> = setpoint    e<val> = early stop");
  Serial.println("  g = mulai | t<num> = set trial berikutnya | r = reset | x = stop | c = param");
  Serial.println("-----------------------------------------");
  Serial.println("TUNING: P dulu -> tambah I -> tambah D");
  Serial.println("=========================================");
  cetakParameter();
  Serial.println("STATUS: SIAP");
}
