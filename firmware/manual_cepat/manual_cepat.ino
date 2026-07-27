/**
 * MANUAL CEPAT - PET FEEDER
 * ==========================
 * Skenario open-loop: sudut bukaan servo tetap 40° sepanjang proses dispensing.
 * Sensor load cell hanya digunakan untuk memantau massa aktual dan menghentikan
 * proses ketika kondisi penghentian tercapai (StopReason=TARGET).
 *
 * Mekanisme kompensasi bridging aktif pada seluruh skenario:
 *   - Kondisi pemicu : kenaikan massa < 0.5 g dalam 3 detik
 *   - Aksi           : servo tutup 300 ms, buka 40° selama 2.000 ms, kembali normal
 *
 * CATATAN REPRODUKSIBILITAS:
 * Firmware ini merupakan implementasi ulang berdasarkan prosedur yang
 * didokumentasikan pada laporan penelitian dan naskah skripsi.
 * Firmware ini bukan file asli yang digunakan selama proses penelitian.
 * Perilaku dan parameter ekuivalen terhadap skenario Manual Cepat pada
 * pengujian yang menghasilkan master_dataset_160.csv.
 *
 * Parameter utama:
 *   - Sudut bukaan utama : 40°
 *   - Early stop         : 0.4 g sebelum setpoint
 *   - Sampling load cell : ~260 ms
 */

#include <ESP32Servo.h>
#include <HX711.h>

// ── Pin ────────────────────────────────────────────────────────────────────
#define SERVO_PIN       18
#define HX711_DATA_PIN  21
#define HX711_CLK_PIN   22

// ── Parameter ──────────────────────────────────────────────────────────────
const float  SERVO_OPEN_DEG      = 40.0f;   // bukaan utama Manual Cepat
const float  SERVO_CLOSE_DEG     =  0.0f;
const float  EARLY_STOP_OFFSET   =  0.4f;   // g sebelum setpoint → tutup servo
const float  BRIDGE_THRESHOLD_G  =  0.5f;   // kenaikan massa minimum dalam window
const uint32_t BRIDGE_WINDOW_MS  = 3000;    // ms deteksi stagnan
const uint32_t BRIDGE_CLOSE_MS   =  300;    // ms servo tutup saat kompensasi
const uint32_t BRIDGE_OPEN_MS    = 2000;    // ms servo buka 40° saat kompensasi

// ── Globals ────────────────────────────────────────────────────────────────
Servo    servo;
HX711    scale;
float    setpoint_g      = 0.0f;
int      bridging_count  = 0;

// ── Fungsi utama ───────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    servo.attach(SERVO_PIN);
    servo.write((int)SERVO_CLOSE_DEG);

    scale.begin(HX711_DATA_PIN, HX711_CLK_PIN);
    scale.set_scale();   // kalibrasi via Serial: kirim 'c<factor>'
    scale.tare();

    Serial.println("Manual Cepat ready. Kirim setpoint: s<gram>");
}

void loop() {
    // Terima perintah Serial
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.startsWith("s")) {
            setpoint_g = cmd.substring(1).toFloat();
            runDispensing();
        }
    }
}

void runDispensing() {
    bridging_count = 0;
    float mass_prev     = scale.get_units(3);
    uint32_t t_prev     = millis();
    float stop_target   = setpoint_g - EARLY_STOP_OFFSET;

    servo.write((int)SERVO_OPEN_DEG);
    Serial.println("START");

    while (true) {
        delay(260);
        float mass_now = scale.get_units(3);

        // Early stop
        if (mass_now >= stop_target) {
            servo.write((int)SERVO_CLOSE_DEG);
            Serial.print("STOP TARGET mass=");
            Serial.print(mass_now);
            Serial.print(" bridging=");
            Serial.println(bridging_count);
            return;
        }

        // Deteksi & kompensasi bridging
        uint32_t t_now = millis();
        if ((t_now - t_prev) >= BRIDGE_WINDOW_MS) {
            if ((mass_now - mass_prev) < BRIDGE_THRESHOLD_G) {
                bridging_count++;
                servo.write((int)SERVO_CLOSE_DEG);
                delay(BRIDGE_CLOSE_MS);
                servo.write((int)SERVO_OPEN_DEG);
                delay(BRIDGE_OPEN_MS);
                servo.write((int)SERVO_OPEN_DEG);
            }
            mass_prev = mass_now;
            t_prev    = t_now;
        }
    }
}
