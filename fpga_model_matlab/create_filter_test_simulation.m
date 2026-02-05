function create_filter_test_simulation()

    % ========== 0. 初始化 ==========
    modelName = 'Filter_Test_Simulation';

    % 使用 find_system 检查模型是否已打开
    existingSystems = find_system('Name', modelName);

    % 如果找到了，说明已打开，关闭它
    if ~isempty(existingSystems)
        bdclose(modelName);
        disp(['📌 已关闭先前打开的模型: ', modelName]);
    end

    % 创建新模型
    new_system(modelName);

    % 设置基本参数
    set_param(modelName, ...
        'SaveFormat', '1', ...                 % SLX 格式
        'StopTime', '1', ...                      % 仿真时间 (秒)
        'SolverType', 'Fixed-step', ...
        'SolverName', 'FixedStepDiscrete');       % 离散求解器
    set_param(modelName, 'SystemSampleTime', '1e-6'); % 基础采样时间 1μs

    disp(['✅ 成功创建模型: ', modelName]);


    % ========== 1. Chirp Signal 扫频信号源 ==========
    add_block('simulink/Sources/Chirp Signal', [modelName '/Chirp']);
    set_param([modelName '/Chirp'], ...
        'Amplitude', '1', ...
        'FrequencyInitial', '1', ...
        'FrequencyTarget', '10000', ...
        'Time', '1', ...
        'SweepMode', 'linear');
    disp('✅ 添加 Chirp 扫频信号源 (1Hz -> 10kHz in 1s)');

    % ========== 2. 待测滤波器（Transfer Function）==========
    wc = 2*pi*2000; % 截止频率 2kHz
    zeta = 0.707;
    num = wc^2;
    den = [1, 2*zeta*wc, wc^2];

    add_block('simulink/Continuous/Transfer Fcn', [modelName '/DUT_Filter']);
    set_param([modelName '/DUT_Filter'], 'TFx', mat2str(num), 'TFy', mat2str(den));

    % 存入模型工作区
    mp = get_param(modelName, 'ModelWorkspace');
    mp.assignin('num', num);
    mp.assignin('den', den);
    mp.assignin('wc', wc);
    mp.assignin('zeta', zeta);
    disp('✅ 添加待测滤波器 DUT (2kHz 二阶低通)');

    % ========== 3. AD 采样模拟：零阶保持 + 量化 ==========
    add_block('simulink/Discrete/Zero-Order Hold', [modelName '/ZOH']);
    set_param([modelName '/ZOH'], 'SampleTime', '1e-6');

    add_block('simulink/Quantization/Quantizer', [modelName '/Quantizer']);
    set_param([modelName '/Quantizer'], ...
        'QuantizationInterval', '2/65536', ...
        'RoundingMode', 'Round to nearest');
    disp('✅ 添加 ZOH + Quantizer 模拟 AD 采样 (1MHz, 16bit)');

    % ========== 4. 数据打包：MATLAB Function ==========
    add_block('simulink/User-Defined Functions/MATLAB Function', [modelName '/Data_Packer']);

    packerCode = [...
        'function pkt = fcn(u, y)\n' ...
        'u_int16 = round(saturation16(u * 32767));\n' ...
        'y_int16 = round(saturation16(y * 32767));\n' ...
        'high_part = bitshift(uint32(u_int16), 16);\n' ...
        'low_part  = bitand(uint32(y_int16), uint32(65535));\n' ...
        'combined  = bitor(high_part, low_part);\n' ...
        'pkt = typecast(combined, ''int32'');\n' ...
        'function out = saturation16(x)\n' ...
        '   out = min(max(x, -32768), 32767);'];

    set_param([modelName '/Data_Packer'], 'FunctionCode', packerCode);
    set_param([modelName '/Data_Packer'], 'NumInputs', '2');
    disp('✅ 添加 Data_Packer 模块（高低16位合并）');

    % ========== 5. UDP Send 或 To File ==========
    try
        add_block('Simulink Support Package for UDP/IP/Sinks/UDP Send', [modelName '/UDP_Send']);
        set_param([modelName '/UDP_Send'], ...
            'RemoteIPPort', '30000', ...
            'RemoteIPAddress', '127.0.0.1', ...
            'DataType', '''int32''', ...
            'MessageID', '0', ...
            'SampleTime', '1e-6');
        disp('✅ 添加 UDP_Send 模块（发送至 127.0.0.1:30000）');
    catch
        warning('UDP/IP 支持包未安装，使用 To File 替代');
        add_block('simulink/Sinks/To File', [modelName '/To_File']);
        set_param([modelName '/To_File'], ...
            'Filename', '''filter_data.mat''', ...
            'VariableName', '''pkt_stream''');
    end

    % ========== 6. 记录原始信号用于分析 ==========
    add_block('simulink/Sinks/To Workspace', [modelName '/ToWs_Input'], ...
        'VariableName', 'u_raw', 'Save2DArray', 'on');
    add_block('simulink/Sinks/To Workspace', [modelName '/ToWs_Output'], ...
        'VariableName', 'y_raw', 'Save2DArray', 'on');
    disp('✅ 添加 To Workspace 模块记录数据');

    % ========== 7. 连接模块 ==========
    connect_blocks(modelName);

    % ========== 8. 保存模型 ==========
    save_system(modelName, [modelName '.slx']);
    set_param(modelName, 'SavedSuccessfully', 'on');
    disp(['✅ 模型已保存为: ', modelName, '.slx']);
    disp('🎉 创建完成！可打开模型进行仿真。');
end

%% 连接函数
function connect_blocks(modelName)
    add_line(modelName, 'Chirp/1', 'DUT_Filter/1');
    add_line(modelName, 'DUT_Filter/1', 'ZOH/1');
    add_line(modelName, 'ZOH/1', 'Quantizer/1');
    add_line(modelName, 'Quantizer/1', 'Data_Packer/y');
    add_line(modelName, 'Chirp/1', 'Data_Packer/u');

    if exist([modelName '/UDP_Send'], 'block') == 5
        add_line(modelName, 'Data_Packer/1', 'UDP_Send/1');
    else
        add_line(modelName, 'Data_Packer/1', 'To_File/1');
    end

    add_line(modelName, 'Chirp/1', 'ToWs_Input/1');
    add_line(modelName, 'Quantizer/1', 'ToWs_Output/1');
end
