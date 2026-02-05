-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2022.2 (lin64) Build 3671981 Fri Oct 14 04:59:54 MDT 2022
-- Date        : Tue Aug 12 02:48:31 2025
-- Host        : yxk2005-ARB19DH running 64-bit Ubuntu 22.04.5 LTS
-- Command     : write_vhdl -force -mode synth_stub
--               /home/yxk2005/Xilinx/Vivado/erace2025_v2/everything_end_v3/everything_end_v2.gen/sources_1/bd/design_1/ip/design_1_top_0_0/design_1_top_0_0_stub.vhdl
-- Design      : design_1_top_0_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg400-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity design_1_top_0_0 is
  Port ( 
    clk : in STD_LOGIC;
    ad : in STD_LOGIC_VECTOR ( 9 downto 0 );
    da : out STD_LOGIC_VECTOR ( 13 downto 0 );
    ad_clk : out STD_LOGIC;
    da_clk : out STD_LOGIC;
    PD : out STD_LOGIC;
    CTRL : out STD_LOGIC_VECTOR ( 2 downto 0 );
    key : in STD_LOGIC;
    SCK : in STD_LOGIC;
    CS : in STD_LOGIC;
    MOSI : in STD_LOGIC;
    MISO : out STD_LOGIC;
    LED : out STD_LOGIC
  );

end design_1_top_0_0;

architecture stub of design_1_top_0_0 is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "clk,ad[9:0],da[13:0],ad_clk,da_clk,PD,CTRL[2:0],key,SCK,CS,MOSI,MISO,LED";
attribute X_CORE_INFO : string;
attribute X_CORE_INFO of stub : architecture is "top,Vivado 2022.2";
begin
end;
