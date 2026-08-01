%% =========================================================
%  ZIEGLER-NICHOLS UNTUK PROSES INTEGRATOR
%  Berdasarkan data Step 1 Response Test
%  =========================================================
%  Plant model: G(s) = R / s  (integrator dengan dead time L)
%  Step response → ramp: y(t) = R × (t - L) untuk t > L
%
%  Rumus Z-N untuk integrating process:
%    PID: Kp = 1.2/(R×L), Ti = 2L, Td = 0.5L
%    Konversi ke kode: Ki = Kp/Ti, Kd = Kp×Td
%  =========================================================

clc; clear; close all;

%% =========================================================
% 1. BACA DATA DARI FILE
%  =========================================================
% Path relatif terhadap root repositori (jalankan dari folder mana saja)
script_path = fileparts(mfilename('fullpath'));
repo_root   = fileparts(fileparts(fileparts(script_path)));
base_path   = fullfile(repo_root, 'data', 'identifikasi_plant');

% File dan trial yang BERSIH (tanpa/minim bridging)
% Format: {filename, trial_number, sudut}
files = {
    '25 derajat.txt', 2, 25;   % 0x bridging
    '30 derajat.txt', 2, 30;   % 1x bridging (ambil sebelum bridging)
    '35 derajat.txt', 1, 35;   % 0x bridging
    '35 derajat.txt', 2, 35;   % 0x bridging
    '40 derajat.txt', 2, 40;   % 0x bridging
    '40 derajat.txt', 3, 40;   % 0x bridging
};

% Threshold untuk deteksi awal aliran
FLOW_THRESHOLD = 0.5;  % gram - di atas noise

% Simpan hasil
results = struct('sudut', {}, 'R', {}, 'L', {}, ...
                 'Kp_zn', {}, 'Ki_zn', {}, 'Kd_zn', {}, ...
                 'Ti_zn', {}, 'Td_zn', {});

%% =========================================================
% 2. PROSES SETIAP TRIAL
%  =========================================================
figure('Name', 'Step 1 - Identifikasi R dan L', ...
       'Position', [100 100 1200 800]);

n_files = size(files, 1);
colors = lines(n_files);

for i = 1:n_files
    fname = files{i, 1};
    trial_num = files{i, 2};
    sudut = files{i, 3};
    
    % --- Baca file ---
    fpath = fullfile(base_path, fname);
    fid = fopen(fpath, 'r');
    raw = textscan(fid, '%s', 'Delimiter', '\n');
    fclose(fid);
    lines_raw = raw{1};
    
    % --- Cari DATA START/END untuk trial ke-N ---
    start_indices = find(contains(lines_raw, '=== DATA START ==='));
    end_indices = find(contains(lines_raw, '=== DATA END ==='));
    
    if trial_num > length(start_indices)
        fprintf('Trial %d tidak ditemukan di %s\n', trial_num, fname);
        continue;
    end
    
    data_start = start_indices(trial_num) + 2; % skip header
    data_end = end_indices(trial_num) - 1;
    
    % --- Parse CSV data ---
    t_ms = [];
    massa = [];
    bridging = [];
    
    for j = data_start:data_end
        line = strtrim(lines_raw{j});
        if startsWith(line, '>>') || isempty(line)
            continue;  % skip bridging event lines
        end
        parts = strsplit(line, ',');
        if length(parts) >= 4
            t_ms(end+1) = str2double(parts{1});
            massa(end+1) = str2double(parts{2});
            bridging(end+1) = str2double(parts{4});
        end
    end
    
    % --- Filter hanya data non-bridging ---
    idx_clean = bridging == 0;
    t_clean = t_ms(idx_clean) / 1000;  % ke detik
    m_clean = massa(idx_clean);
    
    % Pastikan mulai dari t=0
    t_clean = t_clean - t_clean(1);
    
    % --- Hitung Dead Time (L) ---
    % L = waktu sampai massa > threshold
    idx_flow = find(m_clean > FLOW_THRESHOLD, 1, 'first');
    if isempty(idx_flow)
        fprintf('Tidak ada aliran di %s trial %d\n', fname, trial_num);
        continue;
    end
    L = t_clean(idx_flow);
    
    % --- Hitung Slope (R) ---
    % Linear fit pada bagian setelah dead time
    t_ramp = t_clean(idx_flow:end);
    m_ramp = m_clean(idx_flow:end);
    
    % Fit linear: m = R*(t-L) + offset
    p = polyfit(t_ramp, m_ramp, 1);
    R = p(1);  % slope dalam g/s
    
    % --- Z-N untuk integrating process ---
    if L > 0 && R > 0
        Kp_zn = 1.2 / (R * L);
        Ti_zn = 2 * L;
        Td_zn = 0.5 * L;
        Ki_zn = Kp_zn / Ti_zn;  % konversi ke format kode
        Kd_zn = Kp_zn * Td_zn;  % konversi ke format kode
    else
        Kp_zn = NaN; Ti_zn = NaN; Td_zn = NaN;
        Ki_zn = NaN; Kd_zn = NaN;
    end
    
    % --- Simpan hasil ---
    idx = length(results) + 1;
    results(idx).sudut = sudut;
    results(idx).R = R;
    results(idx).L = L;
    results(idx).Kp_zn = Kp_zn;
    results(idx).Ki_zn = Ki_zn;
    results(idx).Kd_zn = Kd_zn;
    results(idx).Ti_zn = Ti_zn;
    results(idx).Td_zn = Td_zn;
    
    % --- Plot ---
    subplot(2, 3, i);
    plot(t_clean, m_clean, 'b-', 'LineWidth', 1.5); hold on;
    
    % Plot garis ramp fit
    t_fit = linspace(0, max(t_clean), 100);
    m_fit = R * (t_fit - L);
    m_fit(t_fit < L) = 0;
    plot(t_fit, m_fit, 'r--', 'LineWidth', 1.5);
    
    % Tandai dead time
    xline(L, 'g--', sprintf('L=%.1fs', L), 'LineWidth', 1.5);
    
    title(sprintf('%d° Trial %d', sudut, trial_num), 'FontSize', 12);
    xlabel('Waktu (s)');
    ylabel('Massa (g)');
    legend('Data aktual', sprintf('Ramp fit (R=%.2f g/s)', R), ...
           'Dead time', 'Location', 'northwest');
    grid on;
    
    fprintf('[%d° T%d] L = %.2f s, R = %.2f g/s → Kp=%.3f Ki=%.4f Kd=%.4f\n', ...
            sudut, trial_num, L, R, Kp_zn, Ki_zn, Kd_zn);
end

sgtitle('Identifikasi Plant: Dead Time (L) dan Slope (R)', 'FontSize', 14);

%% =========================================================
% 3. RATA-RATA PER SUDUT & MAPPING KE ZONA GS
%  =========================================================
fprintf('\n========================================\n');
fprintf('RATA-RATA PER SUDUT\n');
fprintf('========================================\n');

sudut_unik = unique([results.sudut]);
avg_results = struct('sudut', {}, 'R_avg', {}, 'L_avg', {}, ...
                     'Kp_avg', {}, 'Ki_avg', {}, 'Kd_avg', {});

for i = 1:length(sudut_unik)
    s = sudut_unik(i);
    idx = [results.sudut] == s;
    
    R_avg = mean([results(idx).R]);
    L_avg = mean([results(idx).L]);
    Kp_avg = mean([results(idx).Kp_zn]);
    Ki_avg = mean([results(idx).Ki_zn]);
    Kd_avg = mean([results(idx).Kd_zn]);
    
    avg_results(end+1).sudut = s;
    avg_results(end).R_avg = R_avg;
    avg_results(end).L_avg = L_avg;
    avg_results(end).Kp_avg = Kp_avg;
    avg_results(end).Ki_avg = Ki_avg;
    avg_results(end).Kd_avg = Kd_avg;
    
    fprintf('Sudut %d°: R=%.3f g/s, L=%.2f s → Kp=%.3f, Ki=%.4f, Kd=%.4f\n', ...
            s, R_avg, L_avg, Kp_avg, Ki_avg, Kd_avg);
end

%% =========================================================
% 4. MAPPING KE ZONA GAIN SCHEDULING
%  =========================================================
% Zona 1 (error besar >50%): output tinggi → servo ~35-40°
% Zona 2 (error sedang 15-50%): output sedang → servo ~25-30°
% Zona 3 (error kecil <15%): output rendah → servo ~20-25°

fprintf('\n========================================\n');
fprintf('PARAMETER Z-N PER ZONA GAIN SCHEDULING\n');
fprintf('========================================\n');

% Zona 1 → rata-rata dari 35° dan 40°
idx_z1 = [avg_results.sudut] >= 35;
Kp_z1 = mean([avg_results(idx_z1).Kp_avg]);
Ki_z1 = mean([avg_results(idx_z1).Ki_avg]);
Kd_z1 = mean([avg_results(idx_z1).Kd_avg]);
fprintf('ZONA 1 (error >50%%, servo ~35-40°):\n');
fprintf('  Kp1 = %.3f, Ki1 = %.4f, Kd1 = %.4f\n', Kp_z1, Ki_z1, Kd_z1);

% Zona 2 → rata-rata dari 25° dan 30°
idx_z2 = [avg_results.sudut] >= 25 & [avg_results.sudut] <= 30;
Kp_z2 = mean([avg_results(idx_z2).Kp_avg]);
Ki_z2 = mean([avg_results(idx_z2).Ki_avg]);
Kd_z2 = mean([avg_results(idx_z2).Kd_avg]);
fprintf('ZONA 2 (error 15-50%%, servo ~25-30°):\n');
fprintf('  Kp2 = %.3f, Ki2 = %.4f, Kd2 = %.4f\n', Kp_z2, Ki_z2, Kd_z2);

% Zona 3 → pakai data 25° (sudut terkecil yang stabil)
idx_z3 = [avg_results.sudut] == 25;
Kp_z3 = mean([avg_results(idx_z3).Kp_avg]);
Ki_z3 = mean([avg_results(idx_z3).Ki_avg]);
Kd_z3 = mean([avg_results(idx_z3).Kd_avg]);
fprintf('ZONA 3 (error <15%%, servo ~20-25°):\n');
fprintf('  Kp3 = %.3f, Ki3 = %.4f, Kd3 = %.4f\n', Kp_z3, Ki_z3, Kd_z3);

%% =========================================================
% 5. PERBANDINGAN DENGAN PARAMETER SEMPRO
%  =========================================================
fprintf('\n========================================\n');
fprintf('PERBANDINGAN: Z-N vs SEMPRO\n');
fprintf('========================================\n');
fprintf('%-8s %12s %12s %12s\n', '', 'Kp', 'Ki', 'Kd');
fprintf('--- ZONA 1 ---\n');
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Z-N:', Kp_z1, Ki_z1, Kd_z1);
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Sempro:', 8.0, 0.0, 0.0);
fprintf('--- ZONA 2 ---\n');
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Z-N:', Kp_z2, Ki_z2, Kd_z2);
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Sempro:', 5.0, 0.0, 0.03);
fprintf('--- ZONA 3 ---\n');
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Z-N:', Kp_z3, Ki_z3, Kd_z3);
fprintf('%-8s %12.3f %12.4f %12.4f\n', 'Sempro:', 3.0, 0.4, 0.0);

fprintf('\n========================================\n');
fprintf('CATATAN:\n');
fprintf('Parameter Z-N di atas adalah BASELINE AWAL.\n');
fprintf('Fine tuning pada hardware tetap diperlukan\n');
fprintf('karena sifat stokastik material granular.\n');
fprintf('========================================\n');

%% =========================================================
% 6. PLOT PERBANDINGAN R DAN L PER SUDUT
%  =========================================================
figure('Name', 'Plant Characteristics per Angle', ...
       'Position', [100 100 800 400]);

subplot(1,2,1);
bar([avg_results.sudut], [avg_results.R_avg], 'FaceColor', [0.3 0.6 0.9]);
xlabel('Sudut Servo (°)');
ylabel('R - Laju Aliran (g/s)');
title('Slope (R) per Sudut');
grid on;

subplot(1,2,2);
bar([avg_results.sudut], [avg_results.L_avg], 'FaceColor', [0.9 0.5 0.3]);
xlabel('Sudut Servo (°)');
ylabel('L - Dead Time (s)');
title('Dead Time (L) per Sudut');
grid on;

sgtitle('Karakteristik Plant per Sudut Operasi', 'FontSize', 14);
