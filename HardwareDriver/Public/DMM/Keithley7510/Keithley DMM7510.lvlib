<?xml version='1.0' encoding='UTF-8'?>
<Library LVVersion="15008000">
	<Property Name="Instrument Driver" Type="Str">True</Property>
	<Property Name="NI.Lib.Description" Type="Str">LabVIEW Plug and Play instrument driver for Keithley DMM7510 series Instruments.</Property>
	<Property Name="NI.Lib.HelpPath" Type="Str"></Property>
	<Property Name="NI.Lib.Icon" Type="Bin">&amp;1#!!!!!!!)!"1!&amp;!!!-!%!!!@````]!!!!"!!%!!!*)!!!*Q(C=\:3R53N"$):`')+8OA0',E%NO!8(TN3#5]*,8)!#'H!(D!&gt;I1#WY"*QQE*LP^O2\@A2W]JC"'8:0Z\N@7OG\X@6+L@W2&lt;H3YV':H7`/LPUAYWK#=_-@X^DDLQQ:B]'O]T9\D``'0YY_XT`\:3&gt;VDHL`VT`,L&lt;0PV``J`NP^#)_&lt;O9N!8._GKE7+*"?;9N;]\*(KC*XKC*XKC"XKA"XKA"XKA/\KD/\KD/\KD'\KB'\KB'\KBNYYO&gt;+%,H6F*CC?&amp;EK2*AC19&amp;#7XB#@B38A3(F[6]#1]#5`#E`!1II1HY5FY%J[%BW&amp;+?"+?B#@B38B)V5CS&gt;82Y%B\3+_!*?!+?A#@AI;1#HA!A+"9E$J+!I=!:0!1]!5`!Q[-#HI!HY!FY!B\=#HA#HI!HY!FY'.*G*2J.X^(B)9U=(I@(Y8&amp;Y("Z3S_&amp;R?"Q?B]@BI:Q=(I@(A8!+/MF"E$0)#8"?("[(BR]Z0![0Q_0Q/$SYWAJZGZG?JO`I]"A]"I`"9`!90+31Q70Q'$Q'D]&amp;$7BE]"I`"9`!90*33Q70Q'$Q'C&amp;'5]D+3'1/.)%-Q?,D;&lt;L'W3N&amp;)L08[;QY&lt;6&lt;5"62N,N7&amp;5'U'VQ+K&amp;5SW);K*6%[C;'.5(KTZ%";AKL%KI#N3?_Q\&lt;9BOMQV&lt;9!JND5WT3$`X0A@P^8LP&gt;4NPN6JP.2FX8;&lt;6;;&lt;&amp;9;$[@;TK&gt;;D+:D+@6,8VI6[@HUHOX@HZ\?FC_XK_8&lt;Y]PS`@V`8/PXR(X64;=3^`B&lt;.3V$C@(0(0U!&gt;AN(Y]!!!!!</Property>
	<Property Name="NI.Lib.SourceVersion" Type="Int">352354304</Property>
	<Property Name="NI.Lib.Version" Type="Str">1.0.0.0</Property>
	<Property Name="NI.LV.All.SourceOnly" Type="Bool">false</Property>
	<Property Name="NI.SortType" Type="Int">3</Property>
	<Item Name="Private" Type="Folder">
		<Property Name="NI.LibItem.Scope" Type="Int">2</Property>
		<Item Name="Default Instrument Setup.vi" Type="VI" URL="../Private/Default Instrument Setup.vi"/>
	</Item>
	<Item Name="Public" Type="Folder">
		<Property Name="NI.LibItem.Scope" Type="Int">1</Property>
		<Item Name="Action-Status" Type="Folder">
			<Item Name="Trigger" Type="Folder">
				<Item Name="Digital" Type="Folder">
					<Item Name="Configure Digital IO Line Mode.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Configure Digital IO Line Mode.vi"/>
					<Item Name="Read Digital IO Port.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Read Digital IO Port.vi"/>
					<Item Name="Set or Reset Digital IO Line State.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Set or Reset Digital IO Line State.vi"/>
					<Item Name="Write Digital IO Port.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Write Digital IO Port.vi"/>
					<Item Name="Clear Digital Input Line Trigger Event.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Clear Digital Input Line Trigger Event.vi"/>
					<Item Name="Configure Digital Trigger Input Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Configure Digital Trigger Input Line.vi"/>
					<Item Name="Configure Digital Trigger Output Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Configure Digital Trigger Output Line.vi"/>
					<Item Name="Query Digital Input Line Overrun Status.vi" Type="VI" URL="../Public/Action-Status/Trigger/Digital/Query Digital Input Line Overrun Status.vi"/>
				</Item>
				<Item Name="External" Type="Folder">
					<Item Name="Clear External Input Line Trigger Event.vi" Type="VI" URL="../Public/Action-Status/Trigger/External/Clear External Input Line Trigger Event.vi"/>
					<Item Name="Configure External Trigger Input Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/External/Configure External Trigger Input Line.vi"/>
					<Item Name="Configure External Trigger Output Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/External/Configure External Trigger Output Line.vi"/>
					<Item Name="Query External Input Line Overrun Status.vi" Type="VI" URL="../Public/Action-Status/Trigger/External/Query External Input Line Overrun Status.vi"/>
				</Item>
				<Item Name="LAN" Type="Folder">
					<Item Name="Clear LAN Input Line Trigger Event.vi" Type="VI" URL="../Public/Action-Status/Trigger/LAN/Clear LAN Input Line Trigger Event.vi"/>
					<Item Name="Configure LAN Trigger Input Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/LAN/Configure LAN Trigger Input Line.vi"/>
					<Item Name="Configure LAN Trigger Output Line.vi" Type="VI" URL="../Public/Action-Status/Trigger/LAN/Configure LAN Trigger Output Line.vi"/>
					<Item Name="Query LAN Input Line Overrun Status.vi" Type="VI" URL="../Public/Action-Status/Trigger/LAN/Query LAN Input Line Overrun Status.vi"/>
				</Item>
				<Item Name="Blender" Type="Folder">
					<Item Name="Clear Blender Trigger Event.vi" Type="VI" URL="../Public/Action-Status/Trigger/Blender/Clear Blender Trigger Event.vi"/>
					<Item Name="Configure Blender Trigger.vi" Type="VI" URL="../Public/Action-Status/Trigger/Blender/Configure Blender Trigger.vi"/>
					<Item Name="Query Blender Overrun Status.vi" Type="VI" URL="../Public/Action-Status/Trigger/Blender/Query Blender Overrun Status.vi"/>
				</Item>
				<Item Name="Timer" Type="Folder">
					<Item Name="Clear Timer Trigger Event.vi" Type="VI" URL="../Public/Action-Status/Trigger/Timer/Clear Timer Trigger Event.vi"/>
					<Item Name="Configure Timer Trigger.vi" Type="VI" URL="../Public/Action-Status/Trigger/Timer/Configure Timer Trigger.vi"/>
					<Item Name="Enable Timer Trigger State.vi" Type="VI" URL="../Public/Action-Status/Trigger/Timer/Enable Timer Trigger State.vi"/>
					<Item Name="Query Timer Overrun Status.vi" Type="VI" URL="../Public/Action-Status/Trigger/Timer/Query Timer Overrun Status.vi"/>
				</Item>
			</Item>
			<Item Name="Analog Trigger" Type="Folder">
				<Item Name="Configure Edge Trigger.vi" Type="VI" URL="../Public/Action-Status/Analog Trigger/Configure Edge Trigger.vi"/>
				<Item Name="Configure Pulse Width Trigger.vi" Type="VI" URL="../Public/Action-Status/Analog Trigger/Configure Pulse Width Trigger.vi"/>
				<Item Name="Configure Window Trigger.vi" Type="VI" URL="../Public/Action-Status/Analog Trigger/Configure Window Trigger.vi"/>
				<Item Name="Select Analog Trigger Mode.vi" Type="VI" URL="../Public/Action-Status/Analog Trigger/Select Analog Trigger Mode.vi"/>
			</Item>
			<Item Name="Abort.vi" Type="VI" URL="../Public/Action-Status/Abort.vi"/>
			<Item Name="Initiate.vi" Type="VI" URL="../Public/Action-Status/Initiate.vi"/>
			<Item Name="Initiate on Count.vi" Type="VI" URL="../Public/Action-Status/Initiate on Count.vi"/>
			<Item Name="Send Software Trigger.vi" Type="VI" URL="../Public/Action-Status/Send Software Trigger.vi"/>
		</Item>
		<Item Name="Configure" Type="Folder">
			<Item Name="Limit Test" Type="Folder">
				<Item Name="Clear Limit Test Results.vi" Type="VI" URL="../Public/Configure/Limit Test/Clear Limit Test Results.vi"/>
				<Item Name="Configure Limit Test.vi" Type="VI" URL="../Public/Configure/Limit Test/Configure Limit Test.vi"/>
				<Item Name="Enable Limit Test Auto Clear.vi" Type="VI" URL="../Public/Configure/Limit Test/Enable Limit Test Auto Clear.vi"/>
				<Item Name="Enable Limit Test Beeper.vi" Type="VI" URL="../Public/Configure/Limit Test/Enable Limit Test Beeper.vi"/>
				<Item Name="Enable Limit Test.vi" Type="VI" URL="../Public/Configure/Limit Test/Enable Limit Test.vi"/>
				<Item Name="Get Limit Test Values.vi" Type="VI" URL="../Public/Configure/Limit Test/Get Limit Test Values.vi"/>
				<Item Name="Query Limit Test Results.vi" Type="VI" URL="../Public/Configure/Limit Test/Query Limit Test Results.vi"/>
			</Item>
			<Item Name="Math" Type="Folder">
				<Item Name="Configure Math Operation.vi" Type="VI" URL="../Public/Configure/Math/Configure Math Operation.vi"/>
				<Item Name="Enable Math Operation.vi" Type="VI" URL="../Public/Configure/Math/Enable Math Operation.vi"/>
				<Item Name="Configure Measurement Filter.vi" Type="VI" URL="../Public/Configure/Math/Configure Measurement Filter.vi"/>
				<Item Name="Configure Relative Offset.vi" Type="VI" URL="../Public/Configure/Math/Configure Relative Offset.vi"/>
			</Item>
			<Item Name="Trigger Model" Type="Folder">
				<Item Name="Configure Trigger Model Delta Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Configure Trigger Model Delta Branch.vi"/>
				<Item Name="Create  Trigger Model Reset Branch Count Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create  Trigger Model Reset Branch Count Block.vi"/>
				<Item Name="Create Trigger Model Always Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Always Branch.vi"/>
				<Item Name="Create Trigger Model Buffer Clear Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Buffer Clear Block.vi"/>
				<Item Name="Create Trigger Model ConfigList Next Index Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model ConfigList Next Index Block.vi"/>
				<Item Name="Create Trigger Model ConfigList Prev Index Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model ConfigList Prev Index Block.vi"/>
				<Item Name="Create Trigger Model ConfigList Recall Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model ConfigList Recall Block.vi"/>
				<Item Name="Create Trigger Model Constant Delay Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Constant Delay Block.vi"/>
				<Item Name="Create Trigger Model Constant Limit Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Constant Limit Branch.vi"/>
				<Item Name="Create Trigger Model Digital IO Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Digital IO Block.vi"/>
				<Item Name="Create Trigger Model Digitize Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Digitize Block.vi"/>
				<Item Name="Create Trigger Model Dynamic Delay Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Dynamic Delay Block.vi"/>
				<Item Name="Create Trigger Model Dynamic Limit Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Dynamic Limit Branch.vi"/>
				<Item Name="Create Trigger Model Log Event Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Log Event Block.vi"/>
				<Item Name="Create Trigger Model Loop Counter Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Loop Counter Branch.vi"/>
				<Item Name="Create Trigger Model Measure Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Measure Block.vi"/>
				<Item Name="Create Trigger Model Notify Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Notify Block.vi"/>
				<Item Name="Create Trigger Model On Event Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model On Event Branch.vi"/>
				<Item Name="Create Trigger Model Once Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Once Branch.vi"/>
				<Item Name="Create Trigger Model Once Excluded Branch.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Once Excluded Branch.vi"/>
				<Item Name="Create Trigger Model Place Holder Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Place Holder Block.vi"/>
				<Item Name="Create Trigger Model Wait Block.vi" Type="VI" URL="../Public/Configure/Trigger Model/Create Trigger Model Wait Block.vi"/>
				<Item Name="Load Trigger Model ConfigList Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model ConfigList Template.vi"/>
				<Item Name="Load Trigger Model DurationLoop Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model DurationLoop Template.vi"/>
				<Item Name="Load Trigger Model ExternalTrigger Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model ExternalTrigger Template.vi"/>
				<Item Name="Load Trigger Model SimpleLoop Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model SimpleLoop Template.vi"/>
				<Item Name="Load Trigger Model EventLoop Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model EventLoop Template.vi"/>
				<Item Name="Load Trigger Model GradeBinning Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model GradeBinning Template.vi"/>
				<Item Name="Load Trigger Model SortBinning Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model SortBinning Template.vi"/>
				<Item Name="Load Trigger Model Keithley2001 Template.vi" Type="VI" URL="../Public/Configure/Trigger Model/Load Trigger Model Keithley2001 Template.vi"/>
				<Item Name="Query Trigger  Model State.vi" Type="VI" URL="../Public/Configure/Trigger Model/Query Trigger  Model State.vi"/>
				<Item Name="Reset Trigger Model.vi" Type="VI" URL="../Public/Configure/Trigger Model/Reset Trigger Model.vi"/>
			</Item>
			<Item Name="List" Type="Folder">
				<Item Name="Create Configuration List.vi" Type="VI" URL="../Public/Configure/List/Create Configuration List.vi"/>
				<Item Name="Delete Configuration List.vi" Type="VI" URL="../Public/Configure/List/Delete Configuration List.vi"/>
				<Item Name="Get Configuration List Size.vi" Type="VI" URL="../Public/Configure/List/Get Configuration List Size.vi"/>
				<Item Name="Query Configuration List Catalog.vi" Type="VI" URL="../Public/Configure/List/Query Configuration List Catalog.vi"/>
				<Item Name="Query Configuration List.vi" Type="VI" URL="../Public/Configure/List/Query Configuration List.vi"/>
				<Item Name="Recall Configuration List.vi" Type="VI" URL="../Public/Configure/List/Recall Configuration List.vi"/>
				<Item Name="Store Configuration List.vi" Type="VI" URL="../Public/Configure/List/Store Configuration List.vi"/>
			</Item>
			<Item Name="Measurement" Type="Folder">
				<Item Name="Auto Zero Once.vi" Type="VI" URL="../Public/Configure/Measurement/Auto Zero Once.vi"/>
				<Item Name="Configure Autozero State.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Autozero State.vi"/>
				<Item Name="Configure 2Wire Resistance.vi" Type="VI" URL="../Public/Configure/Measurement/Configure 2Wire Resistance.vi"/>
				<Item Name="Configure 4Wire Resistance.vi" Type="VI" URL="../Public/Configure/Measurement/Configure 4Wire Resistance.vi"/>
				<Item Name="Configure AC Current.vi" Type="VI" URL="../Public/Configure/Measurement/Configure AC Current.vi"/>
				<Item Name="Configure AC Voltage.vi" Type="VI" URL="../Public/Configure/Measurement/Configure AC Voltage.vi"/>
				<Item Name="Configure Capacitance.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Capacitance.vi"/>
				<Item Name="Configure DC Current.vi" Type="VI" URL="../Public/Configure/Measurement/Configure DC Current.vi"/>
				<Item Name="Configure DC Voltage Ratio.vi" Type="VI" URL="../Public/Configure/Measurement/Configure DC Voltage Ratio.vi"/>
				<Item Name="Configure DC Voltage.vi" Type="VI" URL="../Public/Configure/Measurement/Configure DC Voltage.vi"/>
				<Item Name="Configure Digitize Current.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Digitize Current.vi"/>
				<Item Name="Configure Digitize Voltage.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Digitize Voltage.vi"/>
				<Item Name="Configure Diode.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Diode.vi"/>
				<Item Name="Configure Frequency.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Frequency.vi"/>
				<Item Name="Configure Line Sync.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Line Sync.vi"/>
				<Item Name="Configure Period.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Period.vi"/>
				<Item Name="Configure Temperature 3Wire RTD Type.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature 3Wire RTD Type.vi"/>
				<Item Name="Configure Temperature 4Wire RTD Type.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature 4Wire RTD Type.vi"/>
				<Item Name="Configure Temperature Thermistor.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature Thermistor.vi"/>
				<Item Name="Configure Temperature Thermocouple.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature Thermocouple.vi"/>
				<Item Name="Configure Temperature User RTD.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature User RTD.vi"/>
				<Item Name="Configure Temperature.vi" Type="VI" URL="../Public/Configure/Measurement/Configure Temperature.vi"/>
				<Item Name="Select Digitize Function.vi" Type="VI" URL="../Public/Configure/Measurement/Select Digitize Function.vi"/>
				<Item Name="Select Measurement Function.vi" Type="VI" URL="../Public/Configure/Measurement/Select Measurement Function.vi"/>
				<Item Name="Set Digitize Measurement Count.vi" Type="VI" URL="../Public/Configure/Measurement/Set Digitize Measurement Count.vi"/>
				<Item Name="Set Measurement Count.vi" Type="VI" URL="../Public/Configure/Measurement/Set Measurement Count.vi"/>
				<Item Name="Configure User Delay.vi" Type="VI" URL="../Public/Configure/Measurement/Configure User Delay.vi"/>
			</Item>
		</Item>
		<Item Name="Data" Type="Folder">
			<Item Name="Reading Buffer" Type="Folder">
				<Item Name="Append Buffer to File in the USB.vi" Type="VI" URL="../Public/Data/Reading Buffer/Append Buffer to File in the USB.vi"/>
				<Item Name="Clear Buffer Statistics.vi" Type="VI" URL="../Public/Data/Reading Buffer/Clear Buffer Statistics.vi"/>
				<Item Name="Clear Buffer.vi" Type="VI" URL="../Public/Data/Reading Buffer/Clear Buffer.vi"/>
				<Item Name="Configure Byte Order.vi" Type="VI" URL="../Public/Data/Reading Buffer/Configure Byte Order.vi"/>
				<Item Name="Configure Data Format.vi" Type="VI" URL="../Public/Data/Reading Buffer/Configure Data Format.vi"/>
				<Item Name="Create User Buffer.vi" Type="VI" URL="../Public/Data/Reading Buffer/Create User Buffer.vi"/>
				<Item Name="Delete User Buffer.vi" Type="VI" URL="../Public/Data/Reading Buffer/Delete User Buffer.vi"/>
				<Item Name="Enable Buffer Logging.vi" Type="VI" URL="../Public/Data/Reading Buffer/Enable Buffer Logging.vi"/>
				<Item Name="Get Buffer Actual Readings Count.vi" Type="VI" URL="../Public/Data/Reading Buffer/Get Buffer Actual Readings Count.vi"/>
				<Item Name="Get Buffer Filling Mode.vi" Type="VI" URL="../Public/Data/Reading Buffer/Get Buffer Filling Mode.vi"/>
				<Item Name="Get Buffer Size.vi" Type="VI" URL="../Public/Data/Reading Buffer/Get Buffer Size.vi"/>
				<Item Name="Get Buffer Statistics.vi" Type="VI" URL="../Public/Data/Reading Buffer/Get Buffer Statistics.vi"/>
				<Item Name="Save Buffer to File in the USB.vi" Type="VI" URL="../Public/Data/Reading Buffer/Save Buffer to File in the USB.vi"/>
				<Item Name="Set ASCII Precision.vi" Type="VI" URL="../Public/Data/Reading Buffer/Set ASCII Precision.vi"/>
				<Item Name="Set Buffer Filling Mode.vi" Type="VI" URL="../Public/Data/Reading Buffer/Set Buffer Filling Mode.vi"/>
				<Item Name="Set Buffer Size.vi" Type="VI" URL="../Public/Data/Reading Buffer/Set Buffer Size.vi"/>
			</Item>
			<Item Name="Fetch from Buffer (Single Point).vi" Type="VI" URL="../Public/Data/Fetch from Buffer (Single Point).vi"/>
			<Item Name="Fetch From Buffer (Multiple Points).vi" Type="VI" URL="../Public/Data/Fetch From Buffer (Multiple Points).vi"/>
			<Item Name="Measure with Configuration (Single Point).vi" Type="VI" URL="../Public/Data/Measure with Configuration (Single Point).vi"/>
			<Item Name="Digitize with Configuration (Single Point).vi" Type="VI" URL="../Public/Data/Digitize with Configuration (Single Point).vi"/>
			<Item Name="Read with Trigger Model (Multiple Points).vi" Type="VI" URL="../Public/Data/Read with Trigger Model (Multiple Points).vi"/>
			<Item Name="Digitize without Trigger Model (Multiple Points).vi" Type="VI" URL="../Public/Data/Digitize without Trigger Model (Multiple Points).vi"/>
			<Item Name="Read without Trigger Model (Multiple Points).vi" Type="VI" URL="../Public/Data/Read without Trigger Model (Multiple Points).vi"/>
		</Item>
		<Item Name="Utility" Type="Folder">
			<Item Name="Calibration" Type="Folder">
				<Item Name="Get Auto Calibration Count.vi" Type="VI" URL="../Public/Utility/Calibration/Get Auto Calibration Count.vi"/>
				<Item Name="Get Auto Calibration Internal Temp.vi" Type="VI" URL="../Public/Utility/Calibration/Get Auto Calibration Internal Temp.vi"/>
				<Item Name="Get Auto Calibration Last Run Time.vi" Type="VI" URL="../Public/Utility/Calibration/Get Auto Calibration Last Run Time.vi"/>
				<Item Name="Get Auto Calibration Next Run Time.vi" Type="VI" URL="../Public/Utility/Calibration/Get Auto Calibration Next Run Time.vi"/>
				<Item Name="Revert Auto Calibration.vi" Type="VI" URL="../Public/Utility/Calibration/Revert Auto Calibration.vi"/>
				<Item Name="Schedule Auto Calibration.vi" Type="VI" URL="../Public/Utility/Calibration/Schedule Auto Calibration.vi"/>
				<Item Name="Start Auto Calibration.vi" Type="VI" URL="../Public/Utility/Calibration/Start Auto Calibration.vi"/>
			</Item>
			<Item Name="System" Type="Folder">
				<Item Name="Change Password.vi" Type="VI" URL="../Public/Utility/System/Change Password.vi"/>
				<Item Name="Clear System Event Log.vi" Type="VI" URL="../Public/Utility/System/Clear System Event Log.vi"/>
				<Item Name="Configure LAN Automatically.vi" Type="VI" URL="../Public/Utility/System/Configure LAN Automatically.vi"/>
				<Item Name="Configure LAN Manually.vi" Type="VI" URL="../Public/Utility/System/Configure LAN Manually.vi"/>
				<Item Name="Configure Power on Setup.vi" Type="VI" URL="../Public/Utility/System/Configure Power on Setup.vi"/>
				<Item Name="Emit Beep.vi" Type="VI" URL="../Public/Utility/System/Emit Beep.vi"/>
				<Item Name="Get Absolute Date Time.vi" Type="VI" URL="../Public/Utility/System/Get Absolute Date Time.vi"/>
				<Item Name="Get Error Count.vi" Type="VI" URL="../Public/Utility/System/Get Error Count.vi"/>
				<Item Name="Get Event Log Count.vi" Type="VI" URL="../Public/Utility/System/Get Event Log Count.vi"/>
				<Item Name="Get GPIB Address.vi" Type="VI" URL="../Public/Utility/System/Get GPIB Address.vi"/>
				<Item Name="Get Internal Temperature.vi" Type="VI" URL="../Public/Utility/System/Get Internal Temperature.vi"/>
				<Item Name="Get LAN MAC Address.vi" Type="VI" URL="../Public/Utility/System/Get LAN MAC Address.vi"/>
				<Item Name="Get Power Line Frequency.vi" Type="VI" URL="../Public/Utility/System/Get Power Line Frequency.vi"/>
				<Item Name="Get Version.vi" Type="VI" URL="../Public/Utility/System/Get Version.vi"/>
				<Item Name="Post Message To Event Log.vi" Type="VI" URL="../Public/Utility/System/Post Message To Event Log.vi"/>
				<Item Name="Save Event Log to File in the USB.vi" Type="VI" URL="../Public/Utility/System/Save Event Log to File in the USB.vi"/>
				<Item Name="Set Absolute Date Time.vi" Type="VI" URL="../Public/Utility/System/Set Absolute Date Time.vi"/>
				<Item Name="Set GPIB Address.vi" Type="VI" URL="../Public/Utility/System/Set GPIB Address.vi"/>
			</Item>
			<Item Name="Status Model" Type="Folder">
				<Item Name="Clear Status.vi" Type="VI" URL="../Public/Utility/Status Model/Clear Status.vi"/>
				<Item Name="Enable Operation Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Enable Operation Event Register.vi"/>
				<Item Name="Enable Questionable Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Enable Questionable Event Register.vi"/>
				<Item Name="Map Event Id to Bit Number in Operation Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Map Event Id to Bit Number in Operation Event Register.vi"/>
				<Item Name="Map Event Id to Bit Number in Questionable Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Map Event Id to Bit Number in Questionable Event Register.vi"/>
				<Item Name="Preset Status.vi" Type="VI" URL="../Public/Utility/Status Model/Preset Status.vi"/>
				<Item Name="Query Operation Event Register Condition.vi" Type="VI" URL="../Public/Utility/Status Model/Query Operation Event Register Condition.vi"/>
				<Item Name="Query Questinable Event Register Condition.vi" Type="VI" URL="../Public/Utility/Status Model/Query Questinable Event Register Condition.vi"/>
				<Item Name="Read Operation Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Read Operation Event Register.vi"/>
				<Item Name="Read Questinable Event Register.vi" Type="VI" URL="../Public/Utility/Status Model/Read Questinable Event Register.vi"/>
			</Item>
			<Item Name="Display" Type="Folder">
				<Item Name="Clear Text on User Swipe Screen.vi" Type="VI" URL="../Public/Utility/Display/Clear Text on User Swipe Screen.vi"/>
				<Item Name="Display User Text Message.vi" Type="VI" URL="../Public/Utility/Display/Display User Text Message.vi"/>
				<Item Name="Select Display Screen.vi" Type="VI" URL="../Public/Utility/Display/Select Display Screen.vi"/>
				<Item Name="Set Display Brightness.vi" Type="VI" URL="../Public/Utility/Display/Set Display Brightness.vi"/>
				<Item Name="Set Display Digits.vi" Type="VI" URL="../Public/Utility/Display/Set Display Digits.vi"/>
				<Item Name="Set Display Reading Format.vi" Type="VI" URL="../Public/Utility/Display/Set Display Reading Format.vi"/>
			</Item>
			<Item Name="Reset.vi" Type="VI" URL="../Public/Utility/Reset.vi"/>
			<Item Name="Save Setup.vi" Type="VI" URL="../Public/Utility/Save Setup.vi"/>
			<Item Name="Recall Setup.vi" Type="VI" URL="../Public/Utility/Recall Setup.vi"/>
			<Item Name="Self-Test.vi" Type="VI" URL="../Public/Utility/Self-Test.vi"/>
			<Item Name="Get Front or Rear Terminal State.vi" Type="VI" URL="../Public/Utility/Get Front or Rear Terminal State.vi"/>
			<Item Name="Error Query.vi" Type="VI" URL="../Public/Utility/Error Query.vi"/>
			<Item Name="Revision Query.vi" Type="VI" URL="../Public/Utility/Revision Query.vi"/>
		</Item>
		<Item Name="Close.vi" Type="VI" URL="../Public/Close.vi"/>
		<Item Name="Initialize.vi" Type="VI" URL="../Public/Initialize.vi"/>
		<Item Name="VI Tree.vi" Type="VI" URL="../Public/VI Tree.vi"/>
	</Item>
</Library>
