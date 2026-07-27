/**
 * GAIN SCHEDULING PID - PET FEEDER
 * ==============================================
 * STRATEGI ANTI-BRIDGING DUA LAPIS:
 *   1. Preventif: getaran periodik (shake) setiap 2 detik
 *      untuk menjaga kontinuitas aliran material granular
 *   2. Reaktif: hammer pulse saat load cell mendeteksi
 *      massa stagnan (delta < 0.5g dalam 3 detik)
 *
 * CATATAN: Pengujian tanpa shake preventif menunjukkan
 * overshoot >10% karena hammer pulse terlalu agresif
 * saat menjadi satu-satunya mekanisme anti-bridging.
 *
 * PRINSIP GAIN SCHEDULING [13]:
 *   Zona 1 Besar  : eNorm > 50%         → Kp1, Ki1, Kd1
 *   Zona 2 Sedang : 15% < eNorm ≤ 50%   → Kp2, Ki2, Kd2
 *   Zona 3 Kecil  : eNorm ≤ 15%         → Kp3, Ki3, Kd3
 *
 * CATATAN TUNING Kd [12][22]:
 *   - Mulai dari Kd=0 dulu (baseline)
 *   - Coba Kd kecil (0.01-0.1) bertahap
 *   - Kalau hasil lebih noise/tidak stabil → kembalikan ke 0
 *   - Noise sensor ±0.5g bisa memperkuat efek derivatif
 *
 * PERINTAH SERIAL:
 *   p1<val>  = Kp zona 1  (contoh: p18.0)
 *   p2<val>  = Kp zona 2  (contoh: p25.0)
 *   p3<val>  = Kp zona 3  (contoh: p33.0)
 *   i1<val>  = Ki zona 1  (contoh: i10.0)
 *   i2<val>  = Ki zona 2  (contoh: i20.1)
 *   i3<val>  = Ki zona 3  (contoh: i30.4)
 *   d1<val>  = Kd zona 1  (contoh: d10.0)
 *   d2<val>  = Kd zona 2  (contoh: d20.05)
 *   d3<val>  = Kd zona 3  (contoh: d30.1)
 *   s<val>   = setpoint gram
 *   e<val>   = early stop margin
 *   g        = mulai dispensing
 *   r        = reset + tare
 *   x        = stop paksa
 *   c        = cetak parameter
 *
 * REFERENSI:
 *   [5]  Ding et al. (2026) - stokastik granular
 *   [6]  Schulze (2021) - bulk solid flow
 *   [10] Zhang et al. (2025) - kriteria akurasi dispensing
 *   [12] Debnath et al. (2022) - parameter PID servo
 *   [13] Åström & Wittenmark (2008) - gain scheduling
 *   [22] Åström & Hägglund (1995) - PID Controllers
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
// PARAMETER SERVO
// ============================================================
const int SUDUT_TUTUP = 0;
const int SUDUT_MIN   = 20;
const int SUDUT_BUKA  = 40;

// ============================================================
// ZONA GALAT [5][6][13]
// ============================================================
const float BATAS_ZONA_BESAR  = 50.0;
const float BATAS_ZONA_KECIL  = 15.0;
const float BATAS_ABSOLUT     = 2.0;

// ============================================================
// PARAMETER GAIN SCHEDULING — Z-N BASELINE
//
// Dihitung dari data Step 1 menggunakan metode Ziegler-Nichols
// untuk proses integrator: Kp=1.2/(R*L), Ti=2L, Td=0.5L
//   Zona 1 → rata-rata R,L dari sudut 35°-40°
//   Zona 2 → rata-rata R,L dari sudut 25°-30°
//   Zona 3 → R,L dari sudut 25°
//
// CATATAN: Ini parameter BASELINE AWAL.
// Fine tuning pada hardware tetap diperlukan
// karena sifat stokastik material granular.
// ============================================================

// Zona 1 — Besar (eNorm > 50%)
float Kp1 = 1.650;
float Ki1 = 3.088;
float Kd1 = 0.279;
float INTEGRAL_MAX_Z1 = 15.0;  // 50/Ki1 ≈ 16, aman di 15

// Zona 2 — Sedang (15-50%)
float Kp2 = 2.30;
float Ki2 = 0.753;
float Kd2 = 0.563;
float INTEGRAL_MAX_Z2 = 30.0;  // 50/Ki2 ≈ 66, cap di 30

// Zona 3 — Kecil (<=15%)
float Kp3 = 2.50;
float Ki3 = 0.181;
float Kd3 = 0.03;   // diturunkan dari Z-N 0.772 — D-spike menyebabkan output=0 di Z3
float INTEGRAL_MAX_Z3 = 30.0;  // 50/Ki3 ≈ 276, cap di 30

// ============================================================
// EARLY STOP [5][6]
// ============================================================
float EARLY_STOP_MARGIN = 0.4;  // Diuji pada margin ketat untuk hasil fair dengan Fixed PID

// ============================================================
// METRIK RESPONSE UNTUK ANALISIS
// ============================================================
const float RISE_LOW_PCT       = 10.0;  // t10 untuk rise time 10-90%
const float RISE_HIGH_PCT      = 90.0;  // t90 untuk rise time 10-90%
const float SETTLING_TOL_PCT   = 5.0;   // band settling ±5% dari setpoint

// ============================================================
// PARAMETER SISTEM
// ============================================================
float               setpoint         = 20.0;
const int           INTERVAL_KONTROL = 100;
const unsigned long TIMEOUT_MS       = 120000;

// ============================================================
// SHAKE PREVENTIF — getaran periodik untuk kontinuitas aliran
// ============================================================
const int SHAKE_INTERVAL_MS = 2000;
const int SHAKE_AMPLITUDO   = 10;
const int SHAKE_DURASI_MS   = 300;

// ============================================================
// ANTI-BRIDGING [5][6]
// ============================================================
const float         BRIDGING_DELTA_MIN = 0.5;
const unsigned long BRIDGING_WINDOW_MS = 3000;
unsigned long       BRIDGING_PULSE_MS  = 2000;
const float         HAMMER_THRESHOLD_G  = 3.0;

// ============================================================
// VARIABEL KONTROL
// ============================================================
float  massaAktual     = 0.0;
float  errorAktual     = 0.0;
float  integralVal     = 0.0;
float  errorSebelumnya = 0.0;
float  outputPID       = 0.0;
int    sudutAktif      = 0;
int    zonaAktif       = 0;
int    zonaSebelumnya  = 0;   // [BARU] untuk deteksi ganti zona

bool          sedangDispensing = false;
unsigned long tKontrolTerakhir = 0;
unsigned long tShakeTerakhir   = 0;
unsigned long tMulaiDispensing = 0;
bool          shakeAktif       = false;
unsigned long tShakeMulai      = 0;
int           nPercobaan       = 0;

// Anti-bridging
float         massaSaatCekBridging = 0.0;
unsigned long tCekBridging         = 0;
bool          bridgingPulseAktif   = false;
unsigned long tBridgingPulseMulai  = 0;
int           nBridgingDeteksi     = 0;

// Laju aliran — untuk early stop adaptif [5][6]
float         massaSebelumnya      = 0.0;
float         lajuAliran           = 0.0;  // gram/detik

// Statistik zona
int hitZona1 = 0;
int hitZona2 = 0;
int hitZona3 = 0;

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

    // Hitung laju aliran (gram/detik) — untuk LOG saja, tidak untuk kontrol [5][6]
    // CATATAN: tidak digunakan untuk early stop karena noise sensor
    // menyebabkan laju tidak akurat pada pembacaan tunggal
    float dt_aliran = INTERVAL_KONTROL / 1000.0;
    lajuAliran = (massaAktual - massaSebelumnya) / dt_aliran;
    if (lajuAliran < 0) lajuAliran = 0;
    massaSebelumnya = massaAktual;

    // Early stop TETAP [5][6][10]
    // Nilai ini dikalibrasi berdasarkan inersia aliran granular
    // Tidak dibuat adaptif karena noise sensor menyebabkan laju tidak akurat
    if (massaAktual >= (setpoint - EARLY_STOP_MARGIN)) {
      stopDispensing("TARGET");
      return;
    }

    // Tentukan zona
    zonaAktif = tentukanZona(errorAktual, setpoint);

    // ============================================================
    // RESET INTEGRAL — hanya saat GANTI zona [DIPERBAIKI dari v2]
    // v2 lama: reset setiap siklus di zona 1&2 (integral tidak efektif)
    // v3 baru: reset hanya saat transisi antar zona
    // ============================================================
    if (zonaAktif != zonaSebelumnya) {
      int zonaLama = zonaSebelumnya;
      integralVal    = 0;
      zonaSebelumnya = zonaAktif;
      Serial.print(">> GANTI ZONA: "); Serial.print(zonaLama);
      Serial.print(" -> "); Serial.print(zonaAktif);
      Serial.print(" @"); Serial.print(massaAktual, 2); Serial.println("g");
    }

    // Anti-bridging [5][6]
    if (sekarang - tCekBridging >= BRIDGING_WINDOW_MS) {
      if ((massaAktual - massaSaatCekBridging) < BRIDGING_DELTA_MIN
          && errorAktual > HAMMER_THRESHOLD_G) {  // tidak hammer dekat target
        nBridgingDeteksi++;
        bridgingPulseAktif  = true;
        tBridgingPulseMulai = sekarang;
        myServo.write(SUDUT_TUTUP);
        Serial.print("BRIDGING #"); Serial.print(nBridgingDeteksi);
        Serial.print(" @"); Serial.print(massaAktual, 2);
        Serial.print("g Z"); Serial.print(zonaAktif);
        Serial.println(" hammer");
      }
      massaSaatCekBridging = massaAktual;
      tCekBridging         = sekarang;
    }
    if (bridgingPulseAktif) {
      unsigned long elapsed = sekarang - tBridgingPulseMulai;
      if (elapsed < 300) {
        myServo.write(SUDUT_TUTUP);
      } else if (elapsed < 300 + BRIDGING_PULSE_MS) {
        myServo.write(SUDUT_BUKA);
      } else {
        bridgingPulseAktif = false;
        myServo.write(sudutAktif);
      }
    }

    // Pilih gain sesuai zona
    float Kp, Ki, Kd;
    switch (zonaAktif) {
      case 1: Kp=Kp1; Ki=Ki1; Kd=Kd1; hitZona1++; break;
      case 2: Kp=Kp2; Ki=Ki2; Kd=Kd2; hitZona2++; break;
      case 3: Kp=Kp3; Ki=Ki3; Kd=Kd3; hitZona3++; break;
      default: Kp=Kp3; Ki=Ki3; Kd=Kd3;
    }

    // Hitung PID diskrit [13][22]
    float dt = INTERVAL_KONTROL / 1000.0;

    // Integral — aktif di semua zona
    // Pembatasan akumulasi integral per zona (disesuaikan dengan Ki)
    float batasIntegral;
    switch (zonaAktif) {
      case 1: batasIntegral = INTEGRAL_MAX_Z1; break;
      case 2: batasIntegral = INTEGRAL_MAX_Z2; break;
      case 3: batasIntegral = INTEGRAL_MAX_Z3; break;
      default: batasIntegral = 15.0;
    }
    integralVal += errorAktual * dt;
    integralVal  = constrain(integralVal, 0, batasIntegral);

    // Derivatif — aktif jika Kd > 0
    // [22]: sensitif noise, gunakan hanya jika hasil membaik
    float derivatif = (errorAktual - errorSebelumnya) / dt;
    errorSebelumnya = errorAktual;

    outputPID = (Kp * errorAktual) + (Ki * integralVal) + (Kd * derivatif);
    outputPID = constrain(outputPID, 0, 100);

    // Mapping output → sudut
    int sudutTarget;
    if (outputPID < 1) {
      sudutTarget = SUDUT_TUTUP;
    } else {
      sudutTarget = map((int)outputPID, 1, 100, SUDUT_MIN, SUDUT_BUKA);
    }
    sudutAktif = sudutTarget;
    if (!shakeAktif && !bridgingPulseAktif) myServo.write(sudutTarget);

    // Log — format lengkap
    Serial.print("DATA,");
    Serial.print(sekarang - tMulaiDispensing);
    Serial.print(","); Serial.print(massaAktual, 2);
    Serial.print(","); Serial.print(errorAktual, 2);
    Serial.print(","); Serial.print((errorAktual/setpoint)*100.0, 1);
    Serial.print(","); Serial.print(outputPID, 1);
    Serial.print(","); Serial.print(sudutTarget);
    Serial.print(",Z"); Serial.print(zonaAktif);
    Serial.print(","); Serial.print(integralVal, 3);
    Serial.print(","); Serial.print(derivatif, 3);
    Serial.print(","); Serial.print(lajuAliran, 2);
    Serial.print(","); Serial.println(nBridgingDeteksi);  // laju aliran g/s + bridging count
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
// TENTUKAN ZONA [5][6][13]
// ============================================================
int tentukanZona(float error, float sp) {
  float eNorm = (error / sp) * 100.0;
  float eAbs  = abs(error);
  if (eNorm > BATAS_ZONA_BESAR)                         return 1;
  if (eNorm <= BATAS_ZONA_KECIL || eAbs <= BATAS_ABSOLUT) return 3;
  return 2;
}

// ============================================================
// PROSES SHAKE PREVENTIF
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
  zonaAktif            = 1;
  zonaSebelumnya       = 0;
  massaSebelumnya      = 0;
  lajuAliran           = 0;
  sedangDispensing     = true;
  tKontrolTerakhir     = millis();
  tShakeTerakhir       = millis();
  tMulaiDispensing     = millis();
  massaSaatCekBridging = 0.0;
  tCekBridging         = millis();
  bridgingPulseAktif   = false;
  nBridgingDeteksi     = 0;
  hitZona1 = 0; hitZona2 = 0; hitZona3 = 0;

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
  Serial.print("Controller: "); Serial.println("Gain Scheduling PID");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);

  Serial.print("Z1_Rule: "); Serial.println("eNorm_gt_50");
  Serial.print("Z1_Kp: "); Serial.println(Kp1, 3);
  Serial.print("Z1_Ki: "); Serial.println(Ki1, 3);
  Serial.print("Z1_Kd: "); Serial.println(Kd1, 3);
  Serial.print("Z1_IntMax: "); Serial.println(INTEGRAL_MAX_Z1, 2);

  Serial.print("Z2_Rule: "); Serial.println("15_lt_eNorm_le_50");
  Serial.print("Z2_Kp: "); Serial.println(Kp2, 3);
  Serial.print("Z2_Ki: "); Serial.println(Ki2, 3);
  Serial.print("Z2_Kd: "); Serial.println(Kd2, 3);
  Serial.print("Z2_IntMax: "); Serial.println(INTEGRAL_MAX_Z2, 2);

  Serial.print("Z3_Rule: "); Serial.println("eNorm_le_15_or_abs_error_le_2g");
  Serial.print("Z3_Kp: "); Serial.println(Kp3, 3);
  Serial.print("Z3_Ki: "); Serial.println(Ki3, 3);
  Serial.print("Z3_Kd: "); Serial.println(Kd3, 3);
  Serial.print("Z3_IntMax: "); Serial.println(INTEGRAL_MAX_Z3, 2);

  Serial.print("ServoMin_deg: "); Serial.println(SUDUT_MIN);
  Serial.print("ServoMax_deg: "); Serial.println(SUDUT_BUKA);
  Serial.print("HammerThreshold_g: "); Serial.println(HAMMER_THRESHOLD_G, 2);
  Serial.print("Sampling_ms: "); Serial.println(INTERVAL_KONTROL);
  Serial.println("DataFormat: DATA,ms,mass_g,error_g,error_pct,output,servo_deg,zone,I,D,flow_gps,bridging_count");
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
  Serial.print("Setpoint   : "); Serial.print(setpoint,1); Serial.println("g");
  Serial.print("Massa akhir: "); Serial.print(massaFinal,2); Serial.println("g");
  Serial.print("Error akhir: "); Serial.print(errorAkhir,2); Serial.println("g");
  Serial.print("Error%     : "); Serial.print(errorPersen,1); Serial.println("%");
  Serial.print("Durasi     : "); Serial.print(durasi); Serial.println("ms");
  Serial.print("Bridging   : "); Serial.print(nBridgingDeteksi); Serial.println("x");
  Serial.print("Zona hits  : Z1="); Serial.print(hitZona1);
  Serial.print(" Z2="); Serial.print(hitZona2);
  Serial.print(" Z3="); Serial.println(hitZona3);

  String statusAkhir;
  if      (abs(errorPersen) <= 5.0) statusAkhir = "AKURAT";
  else if (errorAkhir > 0)          statusAkhir = "OVERSHOOT";
  else                              statusAkhir = "UNDERSHOOT";

  Serial.print("STATUS     : "); Serial.println(statusAkhir);

  Serial.println("=== SUMMARY TRIAL ===");
  Serial.print("Controller: "); Serial.println("Gain Scheduling PID");
  Serial.print("TrialNo: "); Serial.println(nPercobaan);
  Serial.print("Setpoint_g: "); Serial.println(setpoint, 2);
  Serial.print("EarlyStop_g: "); Serial.println(EARLY_STOP_MARGIN, 2);
  Serial.print("StopTarget_g: "); Serial.println(setpoint - EARLY_STOP_MARGIN, 2);
  Serial.print("Z1_Kp: "); Serial.println(Kp1, 3);
  Serial.print("Z1_Ki: "); Serial.println(Ki1, 3);
  Serial.print("Z1_Kd: "); Serial.println(Kd1, 3);
  Serial.print("Z1_IntMax: "); Serial.println(INTEGRAL_MAX_Z1, 2);
  Serial.print("Z2_Kp: "); Serial.println(Kp2, 3);
  Serial.print("Z2_Ki: "); Serial.println(Ki2, 3);
  Serial.print("Z2_Kd: "); Serial.println(Kd2, 3);
  Serial.print("Z2_IntMax: "); Serial.println(INTEGRAL_MAX_Z2, 2);
  Serial.print("Z3_Kp: "); Serial.println(Kp3, 3);
  Serial.print("Z3_Ki: "); Serial.println(Ki3, 3);
  Serial.print("Z3_Kd: "); Serial.println(Kd3, 3);
  Serial.print("Z3_IntMax: "); Serial.println(INTEGRAL_MAX_Z3, 2);
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
  Serial.print("ZonaHit_Z1: "); Serial.println(hitZona1);
  Serial.print("ZonaHit_Z2: "); Serial.println(hitZona2);
  Serial.print("ZonaHit_Z3: "); Serial.println(hitZona3);
  Serial.print("Status: "); Serial.println(statusAkhir);
  Serial.println("Valid: TRUE");
  Serial.print("StopReason: "); Serial.println(alasan);
  Serial.println("=== TRIAL END ===");

  Serial.println("--------------------------------------------");
  Serial.println("r=reset | g=ulangi | c=parameter");
}

// ============================================================
// BACA SERIAL — diperluas untuk Ki1, Ki2, Kd1, Kd2, Kd3
// ============================================================
void bacaSerial() {
  if (!Serial.available()) return;
  String input = Serial.readStringUntil('\n');
  input.trim();
  if (input.length() < 1) return;  // tolak hanya jika benar-benar kosong

  char cmd1 = input.charAt(0);
  // cmd2 dan val hanya valid jika panjang >= 2
  char cmd2 = (input.length() >= 2) ? input.charAt(1) : 0;
  float val = (input.length() >= 3) ? input.substring(2).toFloat() : 0.0;

  // Kp
  if ((cmd1=='p'||cmd1=='P') && cmd2=='1') { Kp1=val; Serial.print("Kp1="); Serial.println(Kp1,2); return; }
  if ((cmd1=='p'||cmd1=='P') && cmd2=='2') { Kp2=val; Serial.print("Kp2="); Serial.println(Kp2,2); return; }
  if ((cmd1=='p'||cmd1=='P') && cmd2=='3') { Kp3=val; Serial.print("Kp3="); Serial.println(Kp3,2); return; }

  // Ki — sekarang semua zona [BARU]
  if ((cmd1=='i'||cmd1=='I') && cmd2=='1') { Ki1=val; Serial.print("Ki1="); Serial.println(Ki1,3); return; }
  if ((cmd1=='i'||cmd1=='I') && cmd2=='2') { Ki2=val; Serial.print("Ki2="); Serial.println(Ki2,3); return; }
  if ((cmd1=='i'||cmd1=='I') && cmd2=='3') { Ki3=val; Serial.print("Ki3="); Serial.println(Ki3,3); return; }

  // Kd — semua zona [BARU]
  if ((cmd1=='d'||cmd1=='D') && cmd2=='1') { Kd1=val; Serial.print("Kd1="); Serial.println(Kd1,3); return; }
  if ((cmd1=='d'||cmd1=='D') && cmd2=='2') { Kd2=val; Serial.print("Kd2="); Serial.println(Kd2,3); return; }
  if ((cmd1=='d'||cmd1=='D') && cmd2=='3') {
    // Proteksi: Kd3 > 0.1 berbahaya — spike derivatif saat bridging release
    if (val > 0.1) {
      Serial.println("PERINGATAN: Kd3 > 0.1 berbahaya pada sistem granular!");
      Serial.println("Gunakan Kd3 <= 0.05. Jika tetap ingin set, ketik 'force' dulu.");
      Serial.print("Kd3 TIDAK diubah, tetap: "); Serial.println(Kd3,3);
    } else {
      Kd3=val; Serial.print("Kd3="); Serial.println(Kd3,3);
    }
    return;
  }

  // Perintah satu karakter
  float val1 = input.substring(1).toFloat();
  switch (cmd1) {
    case 's': case 'S':
      setpoint = val1;
      Serial.print("Setpoint = "); Serial.print(setpoint,1); Serial.println("g"); break;
    case 'e': case 'E':
      EARLY_STOP_MARGIN = val1;
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
    case 'b': case 'B':
      BRIDGING_PULSE_MS = (unsigned long)(val1 * 1000);
      Serial.print("Bridging pulse = "); Serial.print(BRIDGING_PULSE_MS); Serial.println("ms"); break;
    case 't': case 'T': {
      int nextTrial = (int)val1;
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
      Serial.println("CMD: p1/p2/p3 | i1/i2/i3 | d1/d2/d3 | s/e/b/g/t/r/x/c");
  }
}

// ============================================================
// CETAK PARAMETER
// ============================================================
void cetakParameter() {
  Serial.println("======== PARAMETER AKTIF ========");
  Serial.print("Setpoint    : "); Serial.print(setpoint,1); Serial.println("g");
  Serial.println("- Zona 1 Besar (eNorm >50%) -");
  Serial.print("  Kp1="); Serial.print(Kp1,2);
  Serial.print("  Ki1="); Serial.print(Ki1,3);
  Serial.print("  Kd1="); Serial.println(Kd1,3);
  Serial.println("- Zona 2 Sedang (15-50%) -");
  Serial.print("  Kp2="); Serial.print(Kp2,2);
  Serial.print("  Ki2="); Serial.print(Ki2,3);
  Serial.print("  Kd2="); Serial.println(Kd2,3);
  Serial.println("- Zona 3 Kecil (<=15%) -");
  Serial.print("  Kp3="); Serial.print(Kp3,2);
  Serial.print("  Ki3="); Serial.print(Ki3,3);
  Serial.print("  Kd3="); Serial.println(Kd3,3);
  Serial.println("- Sistem -");
  Serial.print("  SUDUT_MIN : "); Serial.print(SUDUT_MIN); Serial.println("deg");
  Serial.print("  SUDUT_BUKA: "); Serial.print(SUDUT_BUKA); Serial.println("deg");
  Serial.print("  EARLY_STOP: SP - "); Serial.print(EARLY_STOP_MARGIN); Serial.println("g");
  Serial.print("  STOP saat : "); Serial.print(setpoint-EARLY_STOP_MARGIN); Serial.println("g");
  Serial.print("  HAMMER_TH : error > "); Serial.print(HAMMER_THRESHOLD_G, 1); Serial.println("g");
  Serial.println("=================================");
}

// ============================================================
// TAMPIL HEADER
// ============================================================
void tampilHeader() {
  Serial.println("=========================================");
  Serial.println(" GAIN SCHEDULING PID ");
  Serial.println(" PET FEEDER - ESP32");
  Serial.println("=========================================");
  Serial.println("Z1 >50%  : Kp1+Ki1+Kd1");
  Serial.println("Z2 15-50%: Kp2+Ki2+Kd2");
  Serial.println("Z3 <=15% : Kp3+Ki3+Kd3 (presisi)");
  Serial.println("-----------------------------------------");
  Serial.println("PERINTAH:");
  Serial.println("  p18.0  = Kp zona 1    i10.0  = Ki zona 1    d10.0  = Kd zona 1");
  Serial.println("  p25.0  = Kp zona 2    i20.1  = Ki zona 2    d20.05 = Kd zona 2");
  Serial.println("  p33.0  = Kp zona 3    i30.4  = Ki zona 3    d30.1  = Kd zona 3");
  Serial.println("  s<g>=setpoint | e<g>=early stop | g=mulai | t<num>=set trial berikutnya | r=reset | x=stop | c=param");
  Serial.println("-----------------------------------------");
  Serial.println("URUTAN TUNING YANG DISARANKAN:");
  Serial.println("  1. Semua Ki=0, Kd=0 → tuning Kp1, Kp2, Kp3 dulu");
  Serial.println("  2. Tambah Ki3 kecil (0.01-0.4) → eliminasi SSE zona 3");
  Serial.println("  3. Coba Ki1, Ki2 kecil jika perlu");
  Serial.println("  4. Coba Kd per zona jika overshoot masih ada");
  Serial.println("     (awasi noise: jika hasil lebih buruk, kembalikan ke 0)");
  Serial.println("=========================================");
  cetakParameter();
  Serial.println("STATUS: SIAP");
}
