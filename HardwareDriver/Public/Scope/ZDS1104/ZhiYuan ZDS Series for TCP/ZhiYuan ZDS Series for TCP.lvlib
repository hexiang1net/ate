<?xml version='1.0' encoding='UTF-8'?>
<Library LVVersion="15008000">
	<Property Name="Instrument Driver" Type="Str">True</Property>
	<Property Name="NI.Lib.DefaultMenu" Type="Str">dir.mnu</Property>
	<Property Name="NI.Lib.Description" Type="Str">This driver configures and takes measurements from the ZhiYuan ZDS Series Oscilloscope. For more inforamtion about this driver, please refer to ZhiYuan ZDS  Series Readme.html</Property>
	<Property Name="NI.Lib.Icon" Type="Bin">&amp;1#!!!!!!!)!"1!&amp;!!!-!%!!!@````]!!!!"!!%!!!(_!!!*Q(C=\&gt;4"=2J"%!81FMM(8]H!21K&gt;!CG11K@!V5&gt;3["2)A21["6,A[+P]7)V&gt;0EE8OWR6;6;.Y-`MT'.WW9CN@9HY(-^PN?_PNP@@([_WD`[0`P@&gt;`U9TZNO&lt;A`ZSCXD;J'J5KV+Z@&lt;PHE9^]Z#-@_=B&lt;XP+7N\TF,3^ZS5N?]J+80/5J4XH+5Z\S\:#(0/1BNSND]&lt;(1G(2--!;DR(A:HO%:HO(R-9:H?):H?)&lt;(E"C?Y2G?Y2E?J]8Q$-`Q$-`QG'K4T(&lt;)?9&lt;(^.%]T&gt;-]T&gt;-]FITG;9#W7*OY49)2L&lt;/^;:\G;2ZPIXG;JXG;JXFU2`-U4`-U4`-Y:&gt;O6XD301]ZDGCC?YCG?YCE?5U@R&amp;%`R&amp;%`R7#[+JXA+ICR9*E?)=F):5$Y54`(Y&amp;]640-640-7D;\N#N?X-1`-YZ$T*ETT*ETT*9YJ)HO2*HO2*(N.']C20]C20]FAKEC&gt;ZEC&gt;"UK+7DT2:/D%.3E(S_.POFNSO5G_3X)\VUXSZ570&gt;A,&amp;OL&amp;AX4+Q&lt;)&gt;9&amp;DH8B9FW17"M&gt;;Q.D&lt;5SM,RTLC]1#RFIYVI3R"M&lt;&gt;[UV&gt;V57&gt;V5E&gt;V5(NV?ZR[B]??,`@YX;\R@6[D=PF%O@T/5[H5RS0RTA=$L(@\W/XW`V[7HVVP,3HH]_F&lt;^\`CXJZ,PU0T]&lt;Y&amp;-_`0?&lt;NU1_[`-%`!!!!!!</Property>
	<Property Name="NI.Lib.SourceVersion" Type="Int">352354304</Property>
	<Property Name="NI.Lib.Version" Type="Str">1.0.0.0</Property>
	<Item Name="Private" Type="Folder">
		<Property Name="NI.LibItem.Scope" Type="Int">2</Property>
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Item Name="Default Instrument Setup.vi" Type="VI" URL="../Private/Default Instrument Setup.vi"/>
	</Item>
	<Item Name="Public" Type="Folder">
		<Property Name="NI.LibItem.Scope" Type="Int">1</Property>
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Item Name="Configure" Type="Folder">
			<Item Name="Acquire" Type="Folder">
				<Item Name="Configure_Acquire.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Acquire/Configure_Acquire.mnu"/>
				<Item Name="Configure Acquire.vi" Type="VI" URL="../Public/Configure/Acquire/Configure Acquire.vi"/>
			</Item>
			<Item Name="Control" Type="Folder">
				<Item Name="Run.vi" Type="VI" URL="../Public/Configure/Control/Run.vi"/>
				<Item Name="Single.vi" Type="VI" URL="../Public/Configure/Control/Single.vi"/>
				<Item Name="Stop.vi" Type="VI" URL="../Public/Configure/Control/Stop.vi"/>
			</Item>
			<Item Name="Math" Type="Folder">
				<Item Name="Configure_Math.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Math/Configure_Math.mnu"/>
				<Item Name="Configure Math (Add).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Add).vi"/>
				<Item Name="Configure Math (Base).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Base).vi"/>
				<Item Name="Configure Math (Diff).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Diff).vi"/>
				<Item Name="Configure Math (Div).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Div).vi"/>
				<Item Name="Configure Math (FFT).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (FFT).vi"/>
				<Item Name="Configure Math (Filter).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Filter).vi"/>
				<Item Name="Configure Math (Int).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Int).vi"/>
				<Item Name="Configure Math (Mul).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Mul).vi"/>
				<Item Name="Configure Math (Sub).vi" Type="VI" URL="../Public/Configure/Math/Configure Math (Sub).vi"/>
				<Item Name="Configure Math.vi" Type="VI" URL="../Public/Configure/Math/Configure Math.vi"/>
			</Item>
			<Item Name="Measurement" Type="Folder">
				<Item Name="Configure_Measurement.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Measurement/Configure_Measurement.mnu"/>
				<Item Name="Clear Measurement.vi" Type="VI" URL="../Public/Configure/Measurement/Clear Measurement.vi"/>
				<Item Name="Configure Measurement Threshold.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Measurement Threshold.vi"/>
			</Item>
			<Item Name="Timebase" Type="Folder">
				<Item Name="Configure_Timebase.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Timebase/Configure_Timebase.mnu"/>
				<Item Name="Configure Timebase ZOOM.vi" Type="VI" URL="../Public/Configure/Timebase/Configure Timebase ZOOM.vi"/>
			</Item>
			<Item Name="Trigger" Type="Folder">
				<Item Name="Configure_Trigger.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Trigger/Configure_Trigger.mnu"/>
				<Item Name="Configure Trigger (Delay).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Delay).vi"/>
				<Item Name="Configure Trigger (Edge).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Edge).vi"/>
				<Item Name="Configure Trigger (Nth Edge).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Nth Edge).vi"/>
				<Item Name="Configure Trigger (Pattern).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Pattern).vi"/>
				<Item Name="Configure Trigger (PRunt).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (PRunt).vi"/>
				<Item Name="Configure Trigger (Pulse).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Pulse).vi"/>
				<Item Name="Configure Trigger (Runt).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Runt).vi"/>
				<Item Name="Configure Trigger (Setup Hold).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Setup Hold).vi"/>
				<Item Name="Configure Trigger (Slope).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Slope).vi"/>
				<Item Name="Configure Trigger (Timeout).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Timeout).vi"/>
				<Item Name="Configure Trigger (Video).vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger (Video).vi"/>
				<Item Name="Configure Trigger Basic.vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger Basic.vi"/>
				<Item Name="Configure Trigger.vi" Type="VI" URL="../Public/Configure/Trigger/Configure Trigger.vi"/>
			</Item>
			<Item Name="Configure.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Configure/Configure.mnu"/>
			<Item Name="Autosetup.vi" Type="VI" URL="../Public/Configure/Autosetup.vi"/>
		</Item>
		<Item Name="Data" Type="Folder">
			<Item Name="Low Level" Type="Folder">
				<Item Name="Data_Low Level.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Data/Low Level/Data_Low Level.mnu"/>
				<Item Name="Fetch Waveform.vi" Type="VI" URL="../Public/Data/Low Level/Fetch Waveform.vi"/>
				<Item Name="Wait for Acquisition Complete.vi" Type="VI" URL="../Public/Data/Low Level/Wait for Acquisition Complete.vi"/>
				<Item Name="Read waveform data sub.vi" Type="VI" URL="../Public/Data/Low Level/Read waveform data sub.vi"/>
			</Item>
			<Item Name="Data.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Data/Data.mnu"/>
			<Item Name="Read Scope Bitmap.vi" Type="VI" URL="../Public/Data/Read Scope Bitmap.vi"/>
			<Item Name="Read Waveform (Multiple).vi" Type="VI" URL="../Public/Data/Read Waveform (Multiple).vi"/>
			<Item Name="Read Waveform (Single).vi" Type="VI" URL="../Public/Data/Read Waveform (Single).vi"/>
			<Item Name="Read Waveform Measurement One Channel.vi" Type="VI" URL="../Public/Data/Read Waveform Measurement One Channel.vi"/>
			<Item Name="Read Waveform Measurement Two Channel.vi" Type="VI" URL="../Public/Data/Read Waveform Measurement Two Channel.vi"/>
			<Item Name="Read Waveform.vi" Type="VI" URL="../Public/Data/Read Waveform.vi"/>
		</Item>
		<Item Name="Utility" Type="Folder">
			<Item Name="Utility.mnu" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/Public/Utility/Utility.mnu"/>
			<Item Name="Error Query.vi" Type="VI" URL="../Public/Utility/Error Query.vi"/>
			<Item Name="Reset.vi" Type="VI" URL="../Public/Utility/Reset.vi"/>
			<Item Name="Revision Query.vi" Type="VI" URL="../Public/Utility/Revision Query.vi"/>
			<Item Name="Self-Test.vi" Type="VI" URL="../Public/Utility/Self-Test.vi"/>
		</Item>
		<Item Name="dir.mnu" Type="Document" URL="../Public/dir.mnu"/>
		<Item Name="Close.vi" Type="VI" URL="../Public/Close.vi"/>
		<Item Name="Initialize.vi" Type="VI" URL="../Public/Initialize.vi"/>
		<Item Name="VI Tree.vi" Type="VI" URL="../Public/VI Tree.vi"/>
	</Item>
	<Item Name="ZhiYuan ZDS Series for TCP Readme.html" Type="Document" URL="/&lt;instrlib&gt;/ZhiYuan ZDS Series for TCP/ZhiYuan ZDS Series for TCP Readme.html"/>
</Library>
