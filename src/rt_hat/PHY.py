# python functions for basic phy accesses
import os
import time
import pyrpio
from pyrpio import i2c, mdio
from rt_hat import FPGA as RT_HAT_FPGA

DEBUG_ENABLE=False

options = pyrpio.RPIOConfigs(gpiomem=True)
# Must be called prior to using any interface
pyrpio.configure(options)
## Used GPIO Pins for clk and data (bit-bang)
clk_pin=4
data_pin=17

# Initialize MDIO bus
mdio_bus = mdio.MDIO(clk_pin,data_pin)
    
# Must be called prior to using any interface
pyrpio.configure(options)

RT_HAT_FPGA.init("/usr/share/InnoRoute/hat_env.sh")


def __debug(message):
	global DEBUG_ENABLE
	if DEBUG_ENABLE:
		print(message)
		
		
def init():
	global mdio_bus
	global RT_HAT_FPGA
	# Configure options

	phy_regs = [{"name": "MII_CONTROL",				"reg_addr": 0x0000,	"dev_addr": 0x00,	"default": 0x1040,	"target": 0x1140,	"access": "R/W",	"comment": "Leaving initial software power-down. Selecting Full-Duplex operation. Restart Auto-Neg."}, # 1340
			#{"name": "MII_STATUS",				"reg_addr": 0x0001,	"dev_addr": 0x00,	"default": 0x7949,	"target": 0x7949,	"access": "R",	"comment": ""},
			#{"name": "PHY_ID_1",				"reg_addr": 0x0002,	"dev_addr": 0x00,	"default": 0x0283,	"target": 0x0283,	"access": "R",	"comment": ""},
			#{"name": "PHY_ID_2",				"reg_addr": 0x0003,	"dev_addr": 0x00,	"default": 0xBC30,	"target": 0xBC30,	"access": "R",	"comment": ""},
			{"name": "AUTONEG_ADV",				"reg_addr": 0x0004,	"dev_addr": 0x00,	"default": 0x01E1,	"target": 0x01E1,	"access": "R/W",	"comment": "Disable Half-Duplex operation."},
			#{"name": "LP_ABILITY",				"reg_addr": 0x0005,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "AUTONEG_EXP",				"reg_addr": 0x0006,	"dev_addr": 0x00,	"default": 0x0064,	"target": 0x0064,	"access": "R",	"comment": ""},
			{"name": "TX_NEXT_PAGE",			"reg_addr": 0x0007,	"dev_addr": 0x00,	"default": 0x2001,	"target": 0x2001,	"access": "R/W",	"comment": ""},
			#{"name": "LP_RX_NEXT_PAGE",			"reg_addr": 0x0008,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "MSTR_SLV_CONTROL",		"reg_addr": 0x0009,	"dev_addr": 0x00,	"default": 0x0200,	"target": 0x0200,	"access": "R/W",	"comment": "Prefer Master - not forcing to be Master."},
			#{"name": "MSTR_SLV_STATUS",			"reg_addr": 0x000A,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "EXT_STATUS",				"reg_addr": 0x000F,	"dev_addr": 0x00,	"default": 0x3000,	"target": 0x3000,	"access": "R",	"comment": ""},
			{"name": "EXT_REG_PTR",			"reg_addr": 0x0010,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0xBA1B,	"access": "R/W",	"comment": ""},
			{"name": "EXT_REGD_ATA",			"reg_addr": 0x0011,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "PHY_CTRL_1",				"reg_addr": 0x0012,	"dev_addr": 0x00,	"default": 0x0002,	"target": 0x0602,	"access": "R/W",	"comment": "Enable Manual+Auto-MDIX, enable diagnistics clock."},
			{"name": "PHY_CTRL_STATUS_1",		"reg_addr": 0x0013,	"dev_addr": 0x00,	"default": 0x1041,	"target": 0x0041,	"access": "R/W",	"comment": ""},
			#{"name": "RX_ER_RCNT",				"reg_addr": 0x0014,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "PHY_CTRL_STATUS_2",		"reg_addr": 0x0015,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "PHY_CTRL_2",				"reg_addr": 0x0016,	"dev_addr": 0x00,	"default": 0x0308,	"target": 0x0F08,	"access": "R/W",	"comment": ""},
			{"name": "PHY_CTRL_3",				"reg_addr": 0x0017,	"dev_addr": 0x00,	"default": 0x3048,	"target": 0x3048,	"access": "R/W",	"comment": ""},
			{"name": "IRQ_MASK",				"reg_addr": 0x0018,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0007,	"access": "R/W",	"comment": "Enable all interrupts."},
			#{"name": "IRQ_STATUS",				"reg_addr": 0x0019,	"dev_addr": 0x00,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "PHY_STATUS_1",			"reg_addr": 0x001A,	"dev_addr": 0x00,	"default": 0x0300,	"target": 0x0300,	"access": "R",	"comment": ""},
			{"name": "LED_CTRL_1",				"reg_addr": 0x001B,	"dev_addr": 0x00,	"default": 0x0001,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "LED_CTRL_2",				"reg_addr": 0x001C,	"dev_addr": 0x00,	"default": 0x210A,	"target": 0x210A,	"access": "R/W",	"comment": ""},
			{"name": "LED_CTRL_3",				"reg_addr": 0x001D,	"dev_addr": 0x00,	"default": 0x1855,	"target": 0x1855,	"access": "R/W",	"comment": ""},
			#{"name": "PHY_STATUS_2",			"reg_addr": 0x001F,	"dev_addr": 0x00,	"default": 0x03FC,	"target": 0x03FC,	"access": "R",	"comment": ""},
			#{"name": "EEE_CAPABILITY",			"reg_addr": 0x8000,	"dev_addr": 0x1E,	"default": 0x0006,	"target": 0x0006,	"access": "R",	"comment": ""},
			{"name": "EEE_ADV",					"reg_addr": 0x8001,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			#{"name": "EEE_LP_ABILITY",			"reg_addr": 0x8002,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "EEE_RSLVD",				"reg_addr": 0x8008,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "MSE_A",					"reg_addr": 0x8402,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "MSE_B",					"reg_addr": 0x8403,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "MSE_C",					"reg_addr": 0x8404,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "MSE_D",					"reg_addr": 0x8405,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "FLD_EN",					"reg_addr": 0x8E27,	"dev_addr": 0x1E,	"default": 0x003D,	"target": 0x0400,	"access": "R/W",	"comment": ""},
			#{"name": "FLD_STAT_LAT",			"reg_addr": 0x8E38,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "RX_MII_CLK_STOP_EN",		"reg_addr": 0x9400,	"dev_addr": 0x1E,	"default": 0x0400,	"target": 0x0400,	"access": "R/W",	"comment": ""},
			#{"name": "PCS_STATUS_1",			"reg_addr": 0x9401,	"dev_addr": 0x1E,	"default": 0x0040,	"target": 0x0040,	"access": "R",	"comment": ""},
			{"name": "FC_EN",					"reg_addr": 0x9403,	"dev_addr": 0x1E,	"default": 0x0001,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "FC_IRQ_EN",				"reg_addr": 0x9406,	"dev_addr": 0x1E,	"default": 0x0001,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "FC_TX_SEL",				"reg_addr": 0x9407,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "FC_MAX_FRM_SIZE",			"reg_addr": 0x9408,	"dev_addr": 0x1E,	"default": 0x05F2,	"target": 0x05F2,	"access": "R/W",	"comment": ""},
			#{"name": "FC_FRM_CNT_H",			"reg_addr": 0x940A,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_FRM_CNT_L",			"reg_addr": 0x940B,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_LEN_ERR_CNT",			"reg_addr": 0x940C,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_ALGN_ERR_CNT",			"reg_addr": 0x940D,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_SYMB_ERR_CNT",			"reg_addr": 0x940E,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_OSZ_CNT",				"reg_addr": 0x940F,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_USZ_CNT",				"reg_addr": 0x9410,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_ODD_CNT",				"reg_addr": 0x9411,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_ODD_PRE_CNT",			"reg_addr": 0x9412,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_DRIBBLE_BITS_CNT",		"reg_addr": 0x9413,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "FC_FALSE_CARRIER_CNT",	"reg_addr": 0x9414,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "FG_EN",					"reg_addr": 0x9415,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "FG_CNTRL_RSTRT",			"reg_addr": 0x9416,	"dev_addr": 0x1E,	"default": 0x0001,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "FG_CONT_MODE_EN",			"reg_addr": 0x9417,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "FG_IRQ_EN",				"reg_addr": 0x9418,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "FG_FRM_LEN",				"reg_addr": 0x941A,	"dev_addr": 0x1E,	"default": 0x006B,	"target": 0x006B,	"access": "R/W",	"comment": ""},
			{"name": "FG_NFRM_H",				"reg_addr": 0x941C,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "FG_NFRM_L",				"reg_addr": 0x941D,	"dev_addr": 0x1E,	"default": 0x0100,	"target": 0x0100,	"access": "R/W",	"comment": ""},
			#{"name": "FG_DONE",					"reg_addr": 0x941E,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "FIFO_SYNC",				"reg_addr": 0x9427,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": "Enable synchronous operation (always except for 1000BASE-T slave mode)."},
			{"name": "SOP_CTRL",				"reg_addr": 0x9428,	"dev_addr": 0x1E,	"default": 0x0034,	"target": 0x0034,	"access": "R/W",	"comment": "SoP detection for TX frames."},
			{"name": "SOP_RX_DEL",				"reg_addr": 0x9429,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "SOP_TX_DEL",				"reg_addr": 0x942A,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "DPTH_MII_BYTE",			"reg_addr": 0x9602,	"dev_addr": 0x1E,	"default": 0x0001,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			#{"name": "LPI_WAKE_ERR_CNT",		"reg_addr": 0xA000,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			{"name": "B_1000_RTRN_EN",			"reg_addr": 0xA001,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "B_10E_En",				"reg_addr": 0xB403,	"dev_addr": 0x1E,	"default": 0x0001,	"target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "B_10_TX_TST_MODE",		"reg_addr": 0xB412,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "B_100_TX_TST_MODE",		"reg_addr": 0xB413,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "CDIAG_RUN",				"reg_addr": 0xBA1B,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "CDIAG_XPAIR_DIS",			"reg_addr": 0xBA1C,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R/W",	"comment": ""},
			#{"name": "CDIAG_DTLD_RSLTS_0",		"reg_addr": 0xBA1D,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_DTLD_RSLTS_1",		"reg_addr": 0xBA1E,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_DTLD_RSLTS_2",		"reg_addr": 0xBA1F,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_DTLD_RSLTS_3",		"reg_addr": 0xBA20,	"dev_addr": 0x1E,	"default": 0x0000,	"target": 0x0000,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_FLT_DIST_0",		"reg_addr": 0xBA21,	"dev_addr": 0x1E,	"default": 0x00FF,	"target": 0x00FF,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_FLT_DIST_1",		"reg_addr": 0xBA22,	"dev_addr": 0x1E,	"default": 0x00FF,	"target": 0x00FF,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_FLT_DIST_2",		"reg_addr": 0xBA23,	"dev_addr": 0x1E,	"default": 0x00FF,	"target": 0x00FF,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_FLT_DIST_3",		"reg_addr": 0xBA24,	"dev_addr": 0x1E,	"default": 0x00FF,	"target": 0x00FF,	"access": "R",	"comment": ""},
			#{"name": "CDIAG_CBL_LEN_EST",		"reg_addr": 0xBA25,	"dev_addr": 0x1E,	"default": 0x00FF,	"target": 0x00FF,	"access": "R",	"comment": ""},
			{"name": "LED_PUL_STR_DUR",			"reg_addr": 0xBC00,	"dev_addr": 0x1E,	"default": 0x0011,	"target": 0x0011,	"access": "R/W",	"comment": ""},
			{"name": "GE_SFT_RST",				"reg_addr": 0xFF0C,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "GE_SFT_RST_CFG_EN",		"reg_addr": 0xFF0D,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0001,	"access": "R/W",	"comment": ""},
			{"name": "GE_CLK_CFG",                "reg_addr": 0xFF1F,    "dev_addr": 0x1E,    "default": 0x0000, "target": 0x0020,    "access": "R/W",    "comment": "Drive recovered clock to GP_CLK pin. Output 25MHz at CLK25_REF."},
			{"name": "GE_RGMII_CFG",			"reg_addr": 0xFF23,	"dev_addr": 0x1E,	"default": 0x0E05, "target": 0x0E05,	"access": "R/W",	"comment": ""},
			{"name": "GE_RMII_CFG",				"reg_addr": 0xFF24,	"dev_addr": 0x1E,	"default": 0x0116, "target": 0x0116,	"access": "R/W",	"comment": ""},
			{"name": "GE_PHY_BASE_CFG",			"reg_addr": 0xFF26,	"dev_addr": 0x1E,	"default": 0x0C86, "target": 0x0F8E,	"access": "R/W",	"comment": ""},
			{"name": "GE_LNK_STAT_INV_EN",		"reg_addr": 0xFF3C,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": ""},
			{"name": "GE_IO_GP_CLK_OR_CNTRL",	"reg_addr": 0xFF3D,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": "Always selected clock to GP_CLK pin (should not make a difference)."},
			{"name": "GE_IO_GP_OUT_OR_CNTRL",	"reg_addr": 0xFF3E,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": ""}, # Set to 0x0003 for RX_SOP on LINK_ST pin
			{"name": "GE_IO_INT_N_OR_CNTRL",	"reg_addr": 0xFF3F,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": "Always interrupt to INT_N pin (should not make a difference)."},
			{"name": "GE_IO_LED_A_OR_CNTRL",	"reg_addr": 0xFF41,	"dev_addr": 0x1E,	"default": 0x0000, "target": 0x0000,	"access": "R/W",	"comment": ""}]

	### MDIO Operations ###

	# Create bus using GPIO 13 clk and 12 data (bit-bang)

	mdio_bus.open()

	# Read register (CLAUSE-45)
	# read_c22_register(pad, reg)
	# pad (int): 5b physical address
	# reg (int): 5b register address
	# mdio_bus.read_c22_register( 0x00, 0x00, 0x10)


	for phy in [0,1,2]:
		__debug(f'################################### Start of PHY#{phy} #######################################')
		for ii in reversed(phy_regs):  # Disable software power-down last!
			if ii["dev_addr"] == 0x00:
				read_val = mdio_bus.read_c22_register(phy, ii["reg_addr"])
			else:
				mdio_bus.write_c22_register(phy, 0x10, ii["reg_addr"])
				read_val = mdio_bus.read_c22_register(phy, 0x11)
			__debug('Name: {0}\tAddr: 0x{1:X}\tValue_hex: 0x{2:X}\t'.format(ii["name"], ii["reg_addr"], read_val))

			if ii["target"] != read_val:  # ii["default"]:
				if "W" in ii["access"]:
					__debug(f'Writing {hex(ii["target"])} to {ii["name"]} at {hex(ii["reg_addr"])}. {ii["comment"]}')
					if ii["dev_addr"] == 0x00:
						mdio_bus.write_c22_register(phy, ii["reg_addr"], ii["target"])
					else:
						mdio_bus.write_c22_register(phy, 0x10, ii["reg_addr"])
						mdio_bus.write_c22_register(phy, 0x11, ii["target"])
					if ii["dev_addr"] == 0x00:
						read_val = mdio_bus.read_c22_register(phy, ii["reg_addr"])
					else:
						mdio_bus.write_c22_register(phy, 0x10, ii["reg_addr"])
						read_val = mdio_bus.read_c22_register(phy, 0x11)
					__debug('Name: {0}\tAddr: 0x{1:X}\tValue_hex: 0x{2:X}\t'.format(ii["name"], ii["reg_addr"], read_val))
					if ii["target"] != read_val:
						__debug('#### WRITE UNSUCCESSFUL! ####')
			__debug('\n')
		__debug(f'#################################### End of PHY#{phy} ########################################')

	# Close up shop
	mdio_bus.close()
	
def mdio_read(mdio_phy_addr, mdio_reg_addr, dev_addr):
	global mdio_bus
	global RT_HAT_FPGA
	# Open mdio bus
	mdio_bus.open()
	# Read register value
	if dev_addr == "0x00":
		# The PHY core registers at Address 0x00 to Address 0x01F can be accessed using the interface specified under Clause 22. 
		read_val = mdio_bus.read_c22_register(mdio_phy_addr, mdio_reg_addr)
	else:
		# the registers at Address 0x1E can be accessed via Register 0x0010 and Register 0x0011 using Clause 22 access.
		mdio_bus.write_c22_register(mdio_phy_addr, 0x10, mdio_reg_addr)
		read_val = mdio_bus.read_c22_register(mdio_phy_addr, 0x11)
	# Cleanup MDIO bus
	mdio_bus.close()
	return read_val
	
def mdio_write(mdio_phy_addr, mdio_reg_addr, dev_addr, mdio_wr_val):
	global mdio_bus
	global RT_HAT_FPGA
	# Open mdio bus
	mdio_bus.open()

	# Read register value
	if dev_addr == "0x00":
		mdio_bus.write_c22_register(mdio_phy_addr, mdio_reg_addr, mdio_wr_val)
	else:
		mdio_bus.write_c22_register(mdio_phy_addr, 0x10, mdio_reg_addr)
		mdio_bus.write_c22_register(mdio_phy_addr, 0x11, mdio_wr_val)
	# Cleanup MDIO bus
	mdio_bus.close()
	return 0
	
def get_link_status(phy_addr):
	# Read PHY_STATUS_1
	phy_reg_addr_PHY_STATUS_1 = int("0x001A", 0) # PHY Register Addr of PHY_STATUS_1
	rd_phy0_PHY_STATUS_1 = mdio_read(phy_addr, phy_reg_addr_PHY_STATUS_1, "0x00") 
	# Read 
	## bitpos 9:7 - HCD_TECH (3b) - Resolved technology after link established: 10M FD: 0b001;  100M FD: 0b011;  1G FD: 0b101  - reset value 0b110
	## bitpos 6 - LINK_STAT (1b) - Link is up: 0b1;  Link is down: 0b0 - reset value 0b0
	bit_mask_int = int("0b0000001111000000", 2)
	bit_shifts = 6

	# extract link speed with bit mask
	phy_link_status = (rd_phy0_PHY_STATUS_1 & bit_mask_int) >> bit_shifts

	if phy_link_status == 12: # reset value
		__debug("PHY "+str(phy_addr) + " Link is down")
		phy_link_up = 0
		phy_link_speed = 0
	elif phy_link_status == 11: # link up: 1G FD
		phy_link_up = 1
		phy_link_speed = 2
	elif phy_link_status == 7: # link up: 100M FD
		phy_link_up = 1
		phy_link_speed = 1
	elif phy_link_status == 3: # link up: 10M FD
		phy_link_up = 1
		phy_link_speed = 0
	else:
		# can happen through delay in the link status, at next poll the link status should be resolved
		__debug("PHY "+str(phy_addr) + " Link status is unknown - bitpos 9:7 - HCD_TECH (3b) & bitpos 6 - LINK_STAT (1b)" + str(bin(phy_link_status)))
		return (0,0)
	__debug("PHY "+str(phy_addr) + " Link is: " + str(phy_link_up) + "  & link speed: " + str(phy_link_speed))
	return (phy_link_up, phy_link_speed)
	
def phy_force_link_speed(phy_addr, phy_link_speed, adv_pause_frames, adv_async_pause_frames):
	global RT_HAT_FPGA
	# Involved registers addresses
	phy_reg_addr_MII_CONTROL = int("0x0000", 0) # PHY Register: MII_CONTROL
	phy_reg_addr_AUTONEG_ADV = int("0x0004", 0) # PHY Register: AUTONEG_ADV
	phy_reg_addr_MSTR_SLV_CONTROL = int("0x0009", 0) # PHY Register: MSTR_SLV_CONTROL


	# Bring PHY to software power down mode for configuration
	phy_reg_rst_val_MII_CONTROL = 0x0800 # bitpos 11: SFT_PD = 1
	mdio_write(phy_addr, phy_reg_addr_MII_CONTROL, "0x00", phy_reg_rst_val_MII_CONTROL)

	sel_adv_pause = (adv_pause_frames << 10) + (adv_async_pause_frames << 11) # bitpos 11: ADV_APAUSE = 1; bitpos 10: ADV_PAUSE = 1;

	if phy_link_speed == 0: # 10M FD
		# advertise 10M FD only
		phy_reg_rst_val_AUTONEG_ADV =  sel_adv_pause + (1 << 6) + 1 # bitpos 8: FD_100_ADV = 0; bitpos 6: FD_10_ADV = 1; SELECTOR_FIELD (5b) =0x1 
		__debug("phy_reg_rst_val_AUTONEG_ADV: " + str(hex(phy_reg_rst_val_AUTONEG_ADV))+"="+str(bin(phy_reg_rst_val_AUTONEG_ADV)))  
		__debug("PHY "+str(phy_addr) + " force link speed: " + str(phy_link_speed))
		mdio_write(phy_addr, phy_reg_addr_AUTONEG_ADV, "0x00", phy_reg_rst_val_AUTONEG_ADV)

		phy_reg_rst_val_MSTR_SLV_CONTROL = 0x0000 # bitpos 8: FD_1000_ADV = 0   
		mdio_write(phy_addr, phy_reg_addr_MSTR_SLV_CONTROL, "0x00", phy_reg_rst_val_MSTR_SLV_CONTROL)

		# terminate software power down mode
		phy_reg_rst_val_MII_CONTROL = 0x1100 # bitpos 13: SPEED_SEL_LSB = 1, bitpos 12: AUTONEG_EN = 1, bitpos 8: DPLX_MODE = 1,  bitpos 6: SPEED_SEL_MSB = 0, 
		mdio_write(phy_addr, phy_reg_addr_MII_CONTROL, "0x00", phy_reg_rst_val_MII_CONTROL)


	elif phy_link_speed == 1: # 100M FD
		# advertise 100M FD only
		phy_reg_rst_val_AUTONEG_ADV =  sel_adv_pause + (1 << 8) + 1 # bitpos 8: FD_100_ADV = 1; bitpos 6: FD_10_ADV = 0; SELECTOR_FIELD (5b) =0x1 
		__debug("phy_reg_rst_val_AUTONEG_ADV: " + str(hex(phy_reg_rst_val_AUTONEG_ADV))+"="+str(bin(phy_reg_rst_val_AUTONEG_ADV)))  
		__debug("PHY "+str(phy_addr) + " force link speed: " + str(phy_link_speed))
		mdio_write(phy_addr, phy_reg_addr_AUTONEG_ADV, "0x00", phy_reg_rst_val_AUTONEG_ADV)
      
		phy_reg_rst_val_MSTR_SLV_CONTROL = 0x0000 # bitpos 8: FD_1000_ADV = 0   
		mdio_write(phy_addr, phy_reg_addr_MSTR_SLV_CONTROL, "0x00", phy_reg_rst_val_MSTR_SLV_CONTROL)

		# terminate software power down mode
		phy_reg_rst_val_MII_CONTROL = 0x3300 # bitpos 13: SPEED_SEL_LSB = 1, bitpos 12: AUTONEG_EN = 1, bitpos 8: DPLX_MODE = 1,  bitpos 6: SPEED_SEL_MSB = 0, 
		mdio_write(phy_addr, phy_reg_addr_MII_CONTROL, "0x00", phy_reg_rst_val_MII_CONTROL)


	elif phy_link_speed == 2: # 1000M FD
		phy_reg_rst_val_AUTONEG_ADV =  sel_adv_pause + 1 # bitpos 8: FD_100_ADV = 0; bitpos 6: FD_10_ADV = 0; SELECTOR_FIELD (5b) =0x1 
		__debug("phy_reg_rst_val_AUTONEG_ADV: " + str(hex(phy_reg_rst_val_AUTONEG_ADV))+"="+str(bin(phy_reg_rst_val_AUTONEG_ADV)))  
		__debug("PHY "+str(phy_addr) + " force link speed: " + str(phy_link_speed))
		mdio_write(phy_addr, phy_reg_addr_AUTONEG_ADV, "0x00", phy_reg_rst_val_AUTONEG_ADV)

		# advertise 1000M FD only - @2DO later with Pause and Asym Pause in the register phy_reg_addr_AUTONEG_ADV with read modify write
		phy_reg_rst_val_MSTR_SLV_CONTROL = 0x0200 # bitpos 9: FD_1000_ADV = 1  
		mdio_write(phy_addr, phy_reg_addr_MSTR_SLV_CONTROL, "0x00", phy_reg_rst_val_MSTR_SLV_CONTROL)
        
		# terminate software power down mode
		phy_reg_rst_val_MII_CONTROL = 0x1140 # bitpos 13: SPEED_SEL_LSB = 1, bitpos 12: AUTONEG_EN = 1, bitpos 8: DPLX_MODE = 1,  bitpos 6: SPEED_SEL_MSB = 0, 
		mdio_write(phy_addr, phy_reg_addr_MII_CONTROL, "0x00", phy_reg_rst_val_MII_CONTROL)

	elif phy_link_speed == 3: # 10/100/1000M FD
		phy_reg_rst_val_AUTONEG_ADV =  sel_adv_pause + (1 << 8) + (1 << 6) + 1 # bitpos 8: FD_100_ADV = 0; bitpos 6: FD_10_ADV = 0; SELECTOR_FIELD (5b) =0x1 
		print("phy_reg_rst_val_AUTONEG_ADV: " + str(hex(phy_reg_rst_val_AUTONEG_ADV))+"="+str(bin(phy_reg_rst_val_AUTONEG_ADV)))  
		print("PHY "+str(phy_addr) + " force link speed: " + str(phy_link_speed))
		mdio_write(phy_addr, phy_reg_addr_AUTONEG_ADV, "0x00", phy_reg_rst_val_AUTONEG_ADV)

		# advertise 1000M FD only - @2DO later with Pause and Asym Pause in the register phy_reg_addr_AUTONEG_ADV with read modify write
		phy_reg_rst_val_MSTR_SLV_CONTROL = 0x0200 # bitpos 9: FD_1000_ADV = 1  
		mdio_write(phy_addr, phy_reg_addr_MSTR_SLV_CONTROL, "0x00", phy_reg_rst_val_MSTR_SLV_CONTROL)
		
		# terminate software power down mode
		phy_reg_rst_val_MII_CONTROL = 0x1140 # bitpos 13: SPEED_SEL_LSB = 0, bitpos 12: AUTONEG_EN = 1, bitpos 8: DPLX_MODE = 1,  bitpos 6: SPEED_SEL_MSB = 1, 
		mdio_write(phy_addr, phy_reg_addr_MII_CONTROL, "0x00", phy_reg_rst_val_MII_CONTROL)
  
	else:
		__debug("Invalid link speed provided")
		return 1
	return 0
	
	
def phy_adv_init(phy_addr, adv_pause_frames, adv_async_pause_frames):
	# Involved registers addresses
	phy_reg_addr_AUTONEG_ADV = int("0x0004", 0) # PHY Register: AUTONEG_ADV
	phy_reg_addr_MSTR_SLV_CONTROL = int("0x0009", 0) # PHY Register: MSTR_SLV_CONTROL

	# advertise 10M FD, 100M FD, 1000M FD
	sel_adv_pause = (adv_pause_frames << 10) + (adv_async_pause_frames << 11) # bitpos 11: ADV_APAUSE = 1; bitpos 10: ADV_PAUSE = 1;
	phy_reg_rst_val_AUTONEG_ADV =  sel_adv_pause + (1<<8) + (1<<6) + 1 # bitpos 8: FD_100_ADV = 1; bitpos 6: FD_10_ADV = 1; SELECTOR_FIELD (5b) =0x1 
	mdio_write(phy_addr, phy_reg_addr_AUTONEG_ADV, "0x00", phy_reg_rst_val_AUTONEG_ADV)
	__debug("INIT: phy_reg_rst_val_AUTONEG_ADV: " + str(hex(phy_reg_rst_val_AUTONEG_ADV))+"="+str(bin(phy_reg_rst_val_AUTONEG_ADV)))  

	# advertise 1000M FD only - @2DO later with Pause and Asym Pause in the register phy_reg_addr_AUTONEG_ADV with read modify write
	phy_reg_rst_val_MSTR_SLV_CONTROL = 0x0200 # bitpos 9: FD_1000_ADV = 1  
	mdio_write(phy_addr, phy_reg_addr_MSTR_SLV_CONTROL, "0x00", phy_reg_rst_val_MSTR_SLV_CONTROL)
	__debug("INIT: phy_reg_rst_val_MSTR_SLV_CONTROL: " + str(hex(phy_reg_rst_val_MSTR_SLV_CONTROL))+"="+str(bin(phy_reg_rst_val_MSTR_SLV_CONTROL)))  

	
def auto():
	global RT_HAT_FPGA
	verbosity_level = 3

	# PHY init
	phy_reg_addr_PHY_CTRL_2 = int("0x0016", 0) # PHY Register: PHY_CTRL_2
	phy_reg_rst_val_PHY_CTRL_2 = 0x0F08 # bitpos 11: DN_SPEED_TO_100_EN = 1; bitpos 10: DN_SPEED_TO_100_EN = 1; bitpos 10: DN_SPEED_TO_100_EN = 1; bitpos 9downto7 : RESERVED = 0b110; bitpos 3downto1: CLK_CNTRL = 0b100
	mdio_write(0, phy_reg_addr_PHY_CTRL_2, "0x00", phy_reg_rst_val_PHY_CTRL_2)
	mdio_write(1, phy_reg_addr_PHY_CTRL_2, "0x00", phy_reg_rst_val_PHY_CTRL_2)
	mdio_write(2, phy_reg_addr_PHY_CTRL_2, "0x00", phy_reg_rst_val_PHY_CTRL_2)

	support_pause_frames = 0
	# check for Interrupts
	# auto control or software controled? if interrupts are enabled => auto control, else (irq_mask = 0) it is controlled by the software

	# Read IRQ_MASK
	phy_reg_addr_IRQ_MASK = int("0x0018", 0) # PHY Register: IRQ_MASK

	## PHY 0: IRQ_MASK
	rd_phy0_IRQ_MASK = mdio_read(0, phy_reg_addr_IRQ_MASK, "0x00")
	## PHY 1: IRQ_MASK
	rd_phy1_IRQ_MASK = mdio_read(1, phy_reg_addr_IRQ_MASK, "0x00")

	if rd_phy0_IRQ_MASK != 0 and rd_phy1_IRQ_MASK != 0:
		# Read IRQ_STAT
		phy_reg_addr_IRQ_STAT = int("0x0019", 0) # PHY Register: IRQ_STAT

		## PHY 0
		rd_phy0_IRQ_STAT = mdio_read(0, phy_reg_addr_IRQ_STAT, "0x00") # clear on read
		## PHY 1 
		rd_phy1_IRQ_STAT = mdio_read(1, phy_reg_addr_IRQ_STAT, "0x00") # clear on read
		
		__debug("Auto Control")
		__debug("IRQ_STAT")
		__debug(hex(rd_phy0_IRQ_STAT))
		__debug(hex(rd_phy1_IRQ_STAT))
	else:
		__debug("Software Controled")
		__debug("IRQ_MASK")
		__debug(hex(rd_phy0_IRQ_MASK))
		__debug(hex(rd_phy1_IRQ_MASK))

        # phy's are software controled (irq_mask's for Port 0 and 1 are set to 0)
		return 0


	if rd_phy0_IRQ_STAT != 0 or rd_phy1_IRQ_STAT != 0 or True:

		# Are both PHY's ac
		# get link status (link_speed, link_up)
		(rd_phy0_link_up, rd_phy0_link_speed) = get_link_status(0)
		(rd_phy1_link_up, rd_phy1_link_speed) = get_link_status(1)

		if rd_phy0_link_up == 1 and rd_phy1_link_up == 1:
			__debug("Both PHY's are up")

			# sync PHY's

			# compare link speed
			if rd_phy0_link_speed != rd_phy1_link_speed:
				__debug("Link Speeds are different")
				if rd_phy0_link_speed < rd_phy1_link_speed:
					# configure PHY 1
					__debug("Configure PHY 1 - Link Speed: " + str(rd_phy1_link_speed) + " is greater than PHY 0 Link Speed: " + str(rd_phy0_link_speed))
						
					phy_addr = 1
					# @2DO: read pause frame advertisement and asym pause frame advertisement from PHY 0 and set it to PHY 1, later if TAP supports pause frames in HW      
					adv_pause_frames = 0
					adv_async_pause_frames = 0
					phy_force_link_speed(phy_addr, rd_phy0_link_speed, adv_pause_frames, adv_async_pause_frames)

					time.sleep(20) # under 3s phy_force_link_speed fails to set the link speed successfully!!!

					# intialize advertisement for the next negotiation
					phy_adv_init(phy_addr, adv_pause_frames, adv_async_pause_frames)
						
					# get link status (link_speed, link_up)
					(rd_phy0_link_up, rd_phy0_link_speed) = get_link_status(0)
					(rd_phy1_link_up, rd_phy1_link_speed) = get_link_status(1)
				else:
					# configure PHY 0
					phy_addr = 0
					# @2DO: read pause frame advertisement and asym pause frame advertisement from PHY 0 and set it to PHY 1, later if TAP supports pause frames in HW      
					adv_pause_frames = 0
					adv_async_pause_frames = 0
					phy_force_link_speed(phy_addr, rd_phy1_link_speed, adv_pause_frames, adv_async_pause_frames)

					time.sleep(20) # under 3s phy_force_link_speed fails to set the link speed successfully!!!

					# intialize advertisement for the next negotiation
					phy_adv_init(phy_addr, adv_pause_frames, adv_async_pause_frames)

					# get link status (link_speed, link_up)
					(rd_phy0_link_up, rd_phy0_link_speed) = get_link_status(0)
					(rd_phy1_link_up, rd_phy1_link_speed) = get_link_status(1)
			else:
				__debug("Link Speeds are equal")


		else:
			__debug("Both PHY's are not up")
			time.sleep(10)
			
			
def set_FPGA(speed,port):
	global RT_HAT_FPGA
	if port==0:
		if speed==0:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x0)
		if speed==1:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x1)
		if speed==2:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x2)
	if port==1:
		if speed==0:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x0<<2)
		if speed==1:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x1<<2)
		if speed==2:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x2<<2)
	if port==2:
		if speed==0:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x0<<4)
		if speed==1:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x1<<4)
		if speed==2:
			RT_HAT_FPGA.reg_write("C_ADDR_NET_SPEED",0x2<<4)
	

