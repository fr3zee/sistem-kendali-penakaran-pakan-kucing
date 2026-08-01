/**
 * SKENARIO 1 — OPEN LOOP CEPAT (Tanpa Kontrol)
 * ===============================================
 * Penelitian: Perancangan dan Implementasi Kontrol PID Adaptif
 *             Gain Scheduling pada Sistem Pakan Kucing Otomatis
 *
 * PRINSIP:
 *   - Servo dibuka ke sudut MAKSIMUM (40°) sejak awal
 *   - Tidak ada algoritma kontrol — aliran secepat mungkin
 *   - Servo ditutup saat massa >= (setpoint - EARLY_STOP_MARGIN)
 *   - Early stop HANYA sebagai safety — bukan kontrol
 *
 * HIPOTESIS:
 *   - Settling time SANGAT CEPAT
 *   - MAE% TINGGI (sering overshoot karena inersia granular)
 *   - Standar deviasi TINGGI (tidak konsisten)
 *
 * METRIK YANG DIREKAM:
 *   - Settling Time (ms) = durasi total dari mulai sampai servo tutup
 *   - Rise Time (ms)     = waktu mencapai 90% setpoint pertama kali
 *   - Massa akhir (g)    = hasil timbangan setelah servo tutup
 *   - MAE% dan status    = akurasi hasil akhir
 *   - Bridging           = jumlah deteksi stagnasi
 *
 * DISERAGAMKAN dengan Skenario lain:
 *   - Pin, kalibrasi, setpoint sama
 *   - SUDUT_BUKA = 40° (sama dengan GS v3 dan Fixed PID v7)
 *   - Anti-bridging tetap aktif (kondisi fisik sama)
 *   - Sampling 100ms (10 Hz)
 *
 * PERINTAH SERIAL:
 *   s<val>  = setpoint gram (contoh: s20)
 *   e<val>  = early stop margin (contoh: e1.0)
 *   g       = mulai dispensing
 *   r       = reset + tare
 *   x       = stop paksa
 *   c       = cetak parameter
 *
 * REFERENSI:
 *   [5]  Ding et al. (2026) - stokastik granular
 *   [6]  Schulze (2021) - bulk solid flow
 *   [10] Zhang et al. (2025) - kriteria akurasi dispensing
 */

#include <ESP32Servo.h>
#include <HX711.h>

// ============================================================
// PIN — SAMA dengan semua skenario
// ============================================================
#define SERVO_PIN      13
#define LOADCELL_DOUT   4
#define LOADCELL_SCK    2

// ============================================================
// KALIBRASI — SAMA dengan semua skenario
// ============================================================
const float FAKTOR_KALIBRASI = 901.0;

// ============================================================
// PARAMETER SERVO — DISERAGAMKAN
// ============================================================
const int SUDUT_TUTUP = 0;
const int SUDUT_BUKA  = 40;   // Sudut penuh — open loop cepat

// ============================================================
// PARAMETER SISTEM
// ============================================================
const int           INTERVAL_SAMPLING = 100;     // ms — 10 Hz, sama dengan skenario lain
const unsigned long TIMEOUT_MS        = 120000;  // ms — batas observasi/safety disamakan

// Anti-bridging — SAMA dengan skenario lain [5][6]
const float         BRIDGING_DELTA_MIN = 0.5;
const unsigned long BRIDGING_WINDOW_MS = 3000;
const unsigned long BRIDGING_PULSE_MS  = 2000;
const float         HAMMER_THRESHOLD_G = 3.0;

// Shake — SAMA dengan skenario lain
const int SHAKE_INTERVAL_MS = 2000;
const int SHAKE_AMPLITUDO   = 10;
const int SHAKE_DURASI_MS   = 300;

// ============================================================
// PARAMETER SKENARIO 1
// ============================================================
float setpoint         = 20.0;
float EARLY_STOP_MARGIN = 0.4;  // gram — FINAL ES 0.4g

// ============================================================
// VARIABEL KONTROL
// ============================================================
float         massaAktual    = 0.0;
bool          sedangDispensing = false;
unsigned long tMulaiDispensing = 0;
unsigned long tSampling        = 0;
int           nPercobaan       = 0;

// Metrik transien operasional
const float RISE_LOW_PCT     = 10.0;
const float RISE_HIGH_PCT    = 90.0;
const float SETTLING_TOL_PCT = 5.0;
unsigned long tRise10Ms = 0;
unsigned long tRise90Ms = 0;
unsigned long tSettlingCandidateMs = 0;
bool          rise10Reached = false;
bool          rise90Reached = false;
bool          settlingCandidateActive = false;
float         maxMassDuringTrial = 0.0;

// Shake
bool          shakeAktif   = false;
unsigned long tShakeTerakhir = 0;
unsigned long tShakeMulai    = 0;

// Anti-bridging
float         massaSaatCekBridging = 0.0;
unsigned long tCekBridging         = 0;
bool          bridgingPulseAktif   = false;
unsigned long tBridgingPulseMulai  = 0;
int           nBridgingDeteksi     = 0;

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

  // Timeout safety
  if (sekarang - tMulaiDispensing > TIMEOUT_MS) {
    stopDispensing("TIMEOUT");
    return;
  }

  // Sampling
  if (sekarang - tSampling >= INTERVAL_SAMPLING) {
    tSampling = sekarang;

    massaAktual = scale.get_units(3);
    if (massaAktual < 0) massaAktual = 0;

    updateResponseMetrics(sekarang);

    // Early stop — satu-satunya feedback [5][6]
    // Ini bukan kontrol — hanya safety agar tidak overflow mangkuk
    if (massaAktual >= (setpoint - EARLY_STOP_MARGIN)) {
      stopDispensing("TARGET");
      return;
    }

    // Anti-bridging — tetap aktif agar kondisi fisik sama [5][6]
    float errorAktual = setpoint - massaAktual;
    if (sekarang - tCekBridging >= BRIDGING_WINDOW_MS) {
      if ((massaAktual - massaSaatCekBridging) < BRIDGING_DELTA_MIN
          && errorAktual > HAMMER_THRESHOLD_G) {
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
        myServo.write(SUDUT_TUTUP);
      } else if (elapsed < 300 + BRIDGING_PULSE_MS) {
        myServo.write(SUDUT_BUKA);   // kembali ke buka penuh
      } else {
        bridgingPulseAktif = false;
        myServo.write(SUDUT_BUKA);   // S1: selalu kembali ke SUDUT_BUKA
      }
    }

    // Log data
    float eNorm = ((setpoint - massaAktual) / setpoint) * 100.0;
    String zona = eNorm > 50.0 ? "Z1" : (eNorm > 15.0 ? "Z2" : "Z3");
    Serial.print("DATA,");
    Serial.print(sekarang - tMulaiDispensing);
    Serial.print(","); Serial.print(massaAktual, 2);
    Serial.print(","); Serial.print(setpoint - massaAktual, 2);
    Serial.print(","); Serial.print(eNorm, 1);
    Serial.print("%,OPEN,"); Serial.print(SUDUT_BUKA);
    Serial.print(","); Serial.println(zona);
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
// PROSES SHAKE — SAMA dengan skenario lain
// ============================================================
void prosesShake(unsigned long sekarang) {
  if (!shakeAktif &&
      sekarang - tShakeTerakhir >= (unsigned long)SHAKE_INTERVAL_MS) {
    shakeAktif     = true;
    tShakeMulai    = sekarang;
    tShakeTerakhir = sekarang;
    if (!bridgingPulseAktif)
      myServo.write(constrain(SUDUT_BUKA + SHAKE_AMPLITUDO, SUDUT_BUKA, 45));
  } else if (shakeAktif &&
             sekarang - tShakeMulai >= (unsigned long)SHAKE_DURASI_MS) {
    shakeAktif = false;
    if (!bridgingPulseAktif) myServo.write(SUDUT_BUKA);
  } else if (shakeAktif &&
             sekarang - tShakeMulai >= (unsigned long)(SHAKE_DURASI_MS / 2)) {
    if (!bridgingPulseAktif) myServo.write(SUDUT_BUKA);
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
  tRise10Ms            = 0;
  tRise90Ms            = 0;
  tSettlingCandidateMs = 0;
  rise10Reached        = false;
  rise90Reached        = false;
  settlingCandidateActive = false;
  maxMassDuringTrial   = 0.0;
  sedangDispensing     = true;
  tMulaiDispensing     = millis();
  tSampling            = tMulaiDispensing;
  tShakeTerakhir       = tMulaiDispensing;
  massaSaatCekBridging = 0.0;
  tCekBridging         = tMulaiDispensing;
  bridgingPulseAktif   = false;
  nBridgingDeteksi     = 0;

  // Buka servo langsung ke maksimum — open loop cepat
  myServo.write(SUDUT_BUKA);

  Serial.println("=== TRIAL START ===");
  Serial.print("Controller: "); Serial.println("Manual Cepat");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);
  Serial.print("Servo_deg: "); Serial.println(SUDUT_BUKA);
  Serial.println("DataFormat: DATA,ms,mass_g,error_g,error_pct,mode,servo_deg,zone");
  Serial.println("=== DATA START ===");
}

// ============================================================
// STOP DISPENSING
// ============================================================
void stopDispensing(String alasan) {
  unsigned long durasi = millis() - tMulaiDispensing;
  sedangDispensing = false;
  myServo.write(SUDUT_TUTUP);
  shakeAktif = false;

  delay(500);
  float massaFinal  = scale.get_units(10);
  if (massaFinal < 0) massaFinal = 0;
  float errorAkhir  = massaFinal - setpoint;
  float errorPersen = (errorAkhir / setpoint) * 100.0;

  if (massaFinal > maxMassDuringTrial) maxMassDuringTrial = massaFinal;
  float maxOvershootG = max(0.0f, maxMassDuringTrial - setpoint);
  float maxOvershootPct = (maxOvershootG / setpoint) * 100.0;
  long timeTo90Ms = rise90Reached ? (long)tRise90Ms : -1;
  long riseTime10_90Ms = (rise10Reached && rise90Reached) ? (long)(tRise90Ms - tRise10Ms) : -1;
  float settlingTolG = setpoint * (SETTLING_TOL_PCT / 100.0);
  long settlingTimeMs = -1;
  if (abs(errorAkhir) <= settlingTolG) {
    settlingTimeMs = settlingCandidateActive ? (long)tSettlingCandidateMs : (long)durasi;
  }

  String statusAkhir;
  if      (abs(errorPersen) <= 5.0) statusAkhir = "AKURAT";
  else if (errorAkhir > 0)          statusAkhir = "OVERSHOOT";
  else                              statusAkhir = "UNDERSHOOT";

  Serial.println("=== SUMMARY TRIAL ===");
  Serial.print("Controller: "); Serial.println("Manual Cepat");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);
  Serial.print("FinalMass_g: "); Serial.println(massaFinal, 2);
  Serial.print("FinalError_g: "); Serial.println(errorAkhir, 2);
  Serial.print("FinalError_pct: "); Serial.println(errorPersen, 2);
  Serial.print("Duration_ms: "); Serial.println(durasi);
  Serial.print("Duration_s: "); Serial.println(durasi / 1000.0, 2);
  Serial.print("TimeTo90_ms: "); Serial.println(timeTo90Ms);
  Serial.print("RiseTime_10_90_ms: "); Serial.println(riseTime10_90Ms);
  Serial.print("SettlingTime_ms: "); Serial.println(settlingTimeMs);
  Serial.print("MaxMass_g: "); Serial.println(maxMassDuringTrial, 2);
  Serial.print("MaxOvershoot_g: "); Serial.println(maxOvershootG, 2);
  Serial.print("MaxOvershoot_pct: "); Serial.println(maxOvershootPct, 2);
  Serial.print("BridgingCount: "); Serial.println(nBridgingDeteksi);
  Serial.print("Status: "); Serial.println(statusAkhir);
  Serial.println("Valid: TRUE");
  Serial.print("StopReason: "); Serial.println(alasan);
  Serial.println("=== TRIAL END ===");
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
      Serial.println("CMD: s/e/g/t/r/x/c");
  }
}

// ============================================================
// CETAK PARAMETER
// ============================================================
void cetakParameter() {
  Serial.println("======== PARAMETER AKTIF ========");
  Serial.println("[SKENARIO 1 - OPEN LOOP CEPAT]");
  Serial.print("Setpoint   : "); Serial.print(setpoint, 1); Serial.println("g");
  Serial.print("Sudut      : "); Serial.print(SUDUT_BUKA); Serial.println("deg (tetap, open loop)");
  Serial.print("EARLY_STOP : SP - "); Serial.print(EARLY_STOP_MARGIN, 2); Serial.println("g");
  Serial.print("STOP saat  : "); Serial.print(setpoint - EARLY_STOP_MARGIN); Serial.println("g");
  Serial.println("Mode       : Tidak ada kontrol — servo penuh dari awal");
  Serial.println("=================================");
}

// ============================================================
// TAMPIL HEADER
// ============================================================
void tampilHeader() {
  Serial.println("=========================================");
  Serial.println(" SKENARIO 1 — OPEN LOOP CEPAT");
  Serial.println(" PET FEEDER - ESP32");
  Serial.println("=========================================");
  Serial.println("Mode: Servo langsung 40deg, tidak ada PID");
  Serial.println("Tujuan: Benchmark kecepatan tanpa kontrol");
  Serial.println("Hipotesis: Cepat tapi akurasi buruk");
  Serial.println("-----------------------------------------");
  Serial.println("PERINTAH:");
  Serial.println("  s<g> = setpoint | e<g> = early stop (default 0.4g)");
  Serial.println("  g = mulai | t<num> = set trial berikutnya | r = reset | x = stop | c = param");
  Serial.println("=========================================");
  cetakParameter();
  Serial.println("STATUS: SIAP");
}
