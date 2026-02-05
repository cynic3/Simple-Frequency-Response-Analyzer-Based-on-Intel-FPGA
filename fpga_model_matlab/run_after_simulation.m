% run_after_simulation.m
% 假设你已经运行了前半段仿真，得到了 raw_stream

Fs = 10000;           % 采样率
Ts = 1/Fs;
N = length(raw_stream);

% 构造时间向量
t_vector = (0:N-1)' * Ts;

% 合成 structure for From Workspace
raw_stream_with_time = timeseries(uint32(raw_stream), t_vector);
% 或者用 cell 数组方式（兼容性更好）：
% raw_stream_with_time = struct('time', t_vector, 'signals', struct('values', raw_stream(:)));
