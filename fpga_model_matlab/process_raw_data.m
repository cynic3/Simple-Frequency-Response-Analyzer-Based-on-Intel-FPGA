function [mag_dB, phase_deg, y_est] = process_raw_data(u_u32)
% PROCESS_RAW_DATA 处理从 FPGA 打包传来的 uint32 数据流
% 输入：
%   u_u32 - Nx1 向量，来自 From Workspace 的原始数据
% 输出：
%   mag_dB     - 幅频响应（dB），长度 N/2+1
%   phase_deg  - 相频响应（度）
%   y_est      - 预测输出信号示例

% 参数设置
Fs = 10000;           % 采样率（根据你的系统调整）
N_fft = 8192;         % FFT长度（可改为2^N）
N_half = N_fft/2 + 1;

% ========== 1. 解包输入数据 ==========
data = double(u_u32(:));  % 转列向量 + double
x_in_u16 = bitshift(bitand(data, uint32(65535)*65536), -16);  % 高16位
y_out_u16 = bitand(data, uint32(65535));                        % 低16位

% 映射到电压 [-5V, 5V]
x_in_v = (x_in_u16 / 65535) * 10 - 5;
y_out_v = (y_out_u16 / 65535) * 10 - 5;

% 截断或补零到 N_fft 长度
if length(x_in_v) < N_fft
    x_in_v = [x_in_v; zeros(N_fft - length(x_in_v), 1)];
    y_out_v = [y_out_v; zeros(N_fft - length(y_out_v), 1)];
else
    x_in_v = x_in_v(1:N_fft);
    y_out_v = y_out_v(1:N_fft);
end

% ========== 2. 希尔伯特变换 + FFT 得频率响应 ==========
x_analytic = hilbert(x_in_v);
y_analytic = hilbert(y_out_v);

X = fft(x_analytic);
Y = fft(y_analytic);

X_half = X(1:N_half);
Y_half = Y(1:N_half);

% 防止除零
epsilon = 1e-10;
H_est = Y_half ./ (X_half + epsilon);

% 输出幅频和相频
mag_dB = 20*log10(abs(H_est));
phase_deg = angle(H_est) * 180/pi;

% ========== 3. 示例：预测一个测试信号的输出 ==========
f_test = 150; % 测试频率
t_test = (0:N_fft-1)' / Fs;
u_test = 2*sin(2*pi*f_test*t_test);  % 输入信号
U_full = fft(u_test);
U_half = U_full(1:N_half);

Y_pred_half = U_half .* H_est;
Y_pred_full = [Y_pred_half; conj(Y_pred_half(end-1:-1:2))];
y_est = real(ifft(Y_pred_full));

end
