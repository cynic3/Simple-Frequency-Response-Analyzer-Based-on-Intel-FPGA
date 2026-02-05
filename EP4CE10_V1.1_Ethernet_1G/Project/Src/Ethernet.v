module Ethernet(
					input reset_n,                           
					input  fpga_gclk,                   
					output e_reset,

               output e_mdc,
					inout  e_mdio,
		
            
					input	 e_rxc,                       //125Mhz ethernet gmii rx clock
					input	 e_rxdv,	
					input	 e_rxer,						
					input  [7:0] e_rxd,        

					input	 e_txc,                     //25Mhz ethernet mii tx clock         
					output e_gtxc,                    //25Mhz ethernet gmii tx clock  
					output e_txen, 
					output e_txer, 					
					output [7:0] e_txd,
			
	
					output [11:0]  sin2_do_unsigned,
					input  [11:0]  ad_in_unsigned,
					output ad_clk,
					output da_clk,
					output da_pd
  
    );
                

wire [31:0] ram_wr_data;
wire [31:0] ram_rd_data;
wire [8:0] ram_wr_addr;
wire [11:0] ram_rd_addr;

assign e_gtxc=clk1;	 
assign e_reset = 1'b1; 

wire [31:0] datain_reg;
         
wire [3:0] tx_state;
wire [3:0] rx_state;
wire [15:0] rx_total_length;          //rx 的IP包的长度
wire [15:0] tx_total_length;          //tx 的IP包的长度
wire [15:0] rx_data_length;           //rx 的UDP的数据包长度
wire [15:0] tx_data_length;           //rx 的UDP的数据包长度

wire data_receive;
reg ram_wr_finish;

reg [31:0] udp_data [6:0];                        //存储发送字符
reg ram_wren_i;
reg [11:0] ram_addr_i;
reg [31:0] ram_data_i;
reg [4:0] i=0;

wire data_o_valid;
wire wea;
wire [11:0] addra;
wire [31:0] dina;

wire       signed[11:0]        sin2_do    ;
wire       signed[11:0]        ad_in      ;

assign sin2_do_unsigned = sin2_do ^ 12'h800;
assign ad_in = ad_in_unsigned ^ 12'h800;
assign ad_clk = clk_50M;
assign da_clk = ~clk_50M;
assign da_pd = 1'd0;

wire       signed[11:0]        cos2_do    ;
wire									sin2_vld    ;
//	wire 		  signed[31:0]       dat_tmp     ;
//	
//	assign dat_tmp = {sin2_do[11:0],20'd0};


assign wea=ram_wren_i;
assign addra=ram_addr_i;
assign dina=ram_data_i;


assign tx_data_length=16'd1104;
assign tx_total_length=16'd1124;

wire clk_50M;
wire pll_clk,tx_clk;
pll_zsj pll1(
	.areset(1'b0),
	.inclk0(fpga_gclk),
	.c0(pll_clk),
	.c1(tx_clk),
	.c2(clk_50M),
	.locked());
	


wire clk0,clk1;
pll_test pll2(
	.areset(1'b0),
	.inclk0(fpga_gclk),
	.c0(clk0),
	.c1(clk1),
	.locked());


wire change_nco = (count == 28'd0);//触发改变nco生成波的频率
wire send_trigger = (count == 28'd900000);//触发udp包发送
wire change_ram = (count == 28'd300000);//触发ram写地址从0开始

reg sender;
always@(posedge clk0)begin
	if(count == 28'd900000)begin
		sender <= 1;
	end
	else begin
		sender <= 0;
	end
end

reg [4:0] flag;//频率状态
reg [10:0] phi_test;//.phi_inc_i对应值
wire [10:0] phi_test1;
reg [27:0] count;
reg [1:0]tmp;

assign phi_test1 = phi_test;

always@(posedge clk_50M or negedge reset_n)
begin	
  if(!reset_n) 
  begin
     ram_wr_finish<=1'b0;
	  ram_addr_i<=0;
	  ram_data_i<=0;
	  i<=0;
  end
  else if(change_ram == 1)begin
	  i<=0;
	  ram_addr_i<=0;
  end
  else begin
     if(i==4096) begin
        ram_wr_finish<=1'b1;
        ram_wren_i<=1'b0;	
     end
     else begin
	     ram_wr_finish<=1'b0;
        ram_wren_i<=1'b1;
		  ram_addr_i<=ram_addr_i+1'b1;
		  ram_data_i<={sin2_do[11:0],4'd0,ad_in[11:0],4'd0};
		  i<=i+1'b1;
	  end
  end 
end 

reg flag1 = 0;
reg consume = 1;
always@(posedge e_rxc)begin
	if(data_o_valid == 1)begin
		flag1 <= 1;
	end
	else if(consume == 0)begin
		flag1 <= 0;
	end
end

always@(posedge clk_50M or negedge reset_n)begin//在仿真时间内平均11个状态的时间
	if(!reset_n)begin
		flag <= 5'd0;
	end
	else begin
		if(flag1 == 1)begin
			phi_test <= 11'd19;
			consume <= 0;
		end
		else if(flag1 == 0)begin
			consume <= 1;
		end
		if(phi_test > 410)begin
			phi_test <= 11'd20;
		end
		else if(change_nco)begin
			phi_test <= phi_test +11'd1;
		end
	end
end

always@(posedge clk_50M)begin
	if (count == 28'd900000)
		count <= 28'd0;
	else 
		count <= count + 1'b1;
end


sin2     u_sin2
(
     .clk                         ( clk_50M  	  ),//此时钟要和写入ram的时钟频率统一，此时为125Mhz
     .reset_n                     ( reset_n    ),
     .clken                       ( 1'b1       ),
  	  .phi_inc_i                   ( phi_test   ),
 	  .fsin_o                      ( sin2_do    ),
	  .fcos_o    						 ( cos2_do    ),
     .out_valid                   ( sin2_vld   )
 );
 
////////udp发送和接收程序/////////////////// 
udp u1(
	.reset_n(reset_n),
	.e_rxc(clk0),
	.e_rxd(e_rxd),
   .e_rxdv(e_rxdv),

	.data_o_valid(data_o_valid),                    //数据接收有效信号,写入RAM/
	.ram_wr_data(ram_wr_data),                      //接收到的32bit数据写入RAM/	
	.rx_total_length(rx_total_length),              //接收IP包的总长度/
	.mydata_num(mydata_num),                        //for  test
	.rx_state(rx_state),                            //for  test
	.rx_data_length(rx_data_length),                //接收IP包的数据长度/	
	.ram_wr_addr(ram_wr_addr),
	.data_receive(data_receive),
	
	.e_txen(e_txen),
	.e_txd(e_txd),
	.e_txer(e_txer),	
	.ram_rd_data(ram_rd_data),                      //RAM读出的32bit数据/
	.tx_state(tx_state),                            //for test
	.datain_reg(datain_reg),                        //for test
	.tx_data_length(tx_data_length),                //发送IP包的数据长度/	
	.tx_total_length(tx_total_length),              //接发送IP包的总长度/
	.ram_rd_addr(ram_rd_addr),
	.send_trigger(sender),
	.phi_test(phi_test1)

	);


//////////ram用于存储以太网接收到的数据或测试数据///////////////////
ram ram_inst
(
	.data			(dina),
	.wrclock		(clk_50M),
	.rdclock		(clk0),
	.rdaddress	(ram_rd_addr),
	.wraddress	(addra),
	.wren			(wea),
	.q				(ram_rd_data)
);



endmodule
