DATABASE_NAME = "Examples"

def initDashboard():
	query = """
CREATE TABLE ex_lp_widget_parameter_types (
  id integer PRIMARY KEY AUTOINCREMENT,
  type text NOT NULL,
  path text NOT NULL
);
INSERT INTO ex_lp_widget_parameter_types VALUES(1,'Tag Realtime','Exchange/Launchpad/Kpi/EmbeddedViews/Dashboard/Configuration/Parameter Types/Tag Realtime');
INSERT INTO ex_lp_widget_parameter_types VALUES(2,'Tag History','Exchange/Launchpad/Kpi/EmbeddedViews/Dashboard/Configuration/Parameter Types/Tag History');
INSERT INTO ex_lp_widget_parameter_types VALUES(3,'String','Exchange/Launchpad/Kpi/EmbeddedViews/Dashboard/Configuration/Parameter Types/String');
INSERT INTO ex_lp_widget_parameter_types VALUES(4,'Dropdown','Exchange/Launchpad/Kpi/EmbeddedViews/Dashboard/Configuration/Parameter Types/Dropdown');

CREATE TABLE ex_lp_widgets (
  id integer PRIMARY KEY AUTOINCREMENT,
  name text NOT NULL,
  path text NOT NULL
);
INSERT INTO ex_lp_widgets VALUES(1,'Simple Gauge','Exchange/Launchpad/Kpi/Components/SimpleGauge');
INSERT INTO ex_lp_widgets VALUES(2,'Value','Exchange/Launchpad/Kpi/Components/ValueUnitLabel');
INSERT INTO ex_lp_widgets VALUES(3,'Sparkline','Exchange/Launchpad/Kpi/Components/Sparkline');
INSERT INTO ex_lp_widgets VALUES(4,'Line Chart','Exchange/Launchpad/Kpi/Components/LineChart');
INSERT INTO ex_lp_widgets VALUES(5,'Daily Production','Exchange/Launchpad/Kpi/Components/DailyProduction');
INSERT INTO ex_lp_widgets VALUES(6,'Moving Analog Indicator','Exchange/Launchpad/Kpi/Components/MovingAnalogIndicator');
INSERT INTO ex_lp_widgets VALUES(7,'Notepad','Exchange/Launchpad/Kpi/Components/Notepad');
INSERT INTO ex_lp_widgets VALUES(8,'Progress Bar','Exchange/Launchpad/Kpi/Components/ProgressBar');
INSERT INTO ex_lp_widgets VALUES(9,'Progress KPI','Exchange/Launchpad/Kpi/Components/ProgressKpi');
INSERT INTO ex_lp_widgets VALUES(10,'Bar Chart','Exchange/Launchpad/Kpi/Components/BarChart');

CREATE TABLE ex_lp_widget_parameters (
  id integer PRIMARY KEY AUTOINCREMENT,
  widget_id integer NOT NULL,
  parameter_name text NOT NULL,
  parameter text NOT NULL,
  parameter_type_id integer NOT NULL,
  default_value text,
  configuration text,
  FOREIGN KEY (widget_id) REFERENCES ex_lp_widgets (id) ON DELETE CASCADE,
  FOREIGN KEY (parameter_type_id) REFERENCES ex_lp_widget_parameter_types (id)
);
INSERT INTO ex_lp_widget_parameters VALUES(1,1,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(2,2,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(3,3,'Tag','path',2,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(4,4,'Tag 1','path1',2,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(5,4,'Tag 2','path2',2,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(6,4,'Title','title',3,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(7,5,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(8,6,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(9,7,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(10,8,'Tag','path',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(11,9,'Folder Path','folderPath',1,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(12,10,'Tag 1','path1',2,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(13,10,'Tag 2','path2',2,'',NULL);
INSERT INTO ex_lp_widget_parameters VALUES(14,3,'Aggregation Mode','aggMode',4,'Average','{\"options\": [   {     "value": "Average",     "label": "Average"   },   {     "value": "MinMax",     "label": "MinMax"   },   {     "value": "LastValue",     "label": "LastValue"   },   {     "value": "SimpleAverage",     "label": "SimpleAverage"   },   {     "value": "Sum",     "label": "Sum"   },   {     "value": "Minimum",     "label": "Minimum"   },   {     "value": "Maximum",     "label": "Maximum"   },   {     "value": "DurationOn",     "label": "DurationOn"   },   {     "value": "DurationOff",     "label": "DurationOff"   },   {     "value": "CountOn",     "label": "CountOn"   },   {     "value": "CountOff",     "label": "CountOff"   },   {     "value": "Count",     "label": "Count"   },   {     "value": "Range",     "label": "Range"   },   {     "value": "Variance",     "label": "Variance"   },   {     "value": "StdDev",     "label": "StdDev"   },   {     "value": "PctGood",     "label": "PctGood"   },   {     "value": "PctBad",     "label": "PctBad"   } ]}');
INSERT INTO ex_lp_widget_parameters VALUES(15,4,'Aggregation Mode','aggMode',4,'Average','{\"options\": [   {     "value": "Average",     "label": "Average"   },   {     "value": "MinMax",     "label": "MinMax"   },   {     "value": "LastValue",     "label": "LastValue"   },   {     "value": "SimpleAverage",     "label": "SimpleAverage"   },   {     "value": "Sum",     "label": "Sum"   },   {     "value": "Minimum",     "label": "Minimum"   },   {     "value": "Maximum",     "label": "Maximum"   },   {     "value": "DurationOn",     "label": "DurationOn"   },   {     "value": "DurationOff",     "label": "DurationOff"   },   {     "value": "CountOn",     "label": "CountOn"   },   {     "value": "CountOff",     "label": "CountOff"   },   {     "value": "Count",     "label": "Count"   },   {     "value": "Range",     "label": "Range"   },   {     "value": "Variance",     "label": "Variance"   },   {     "value": "StdDev",     "label": "StdDev"   },   {     "value": "PctGood",     "label": "PctGood"   },   {     "value": "PctBad",     "label": "PctBad"   } ]}');
INSERT INTO ex_lp_widget_parameters VALUES(16,10,'Aggregation Mode','aggMode',4,'Average','{\"options\": [   {     "value": "Average",     "label": "Average"   },   {     "value": "MinMax",     "label": "MinMax"   },   {     "value": "LastValue",     "label": "LastValue"   },   {     "value": "SimpleAverage",     "label": "SimpleAverage"   },   {     "value": "Sum",     "label": "Sum"   },   {     "value": "Minimum",     "label": "Minimum"   },   {     "value": "Maximum",     "label": "Maximum"   },   {     "value": "DurationOn",     "label": "DurationOn"   },   {     "value": "DurationOff",     "label": "DurationOff"   },   {     "value": "CountOn",     "label": "CountOn"   },   {     "value": "CountOff",     "label": "CountOff"   },   {     "value": "Count",     "label": "Count"   },   {     "value": "Range",     "label": "Range"   },   {     "value": "Variance",     "label": "Variance"   },   {     "value": "StdDev",     "label": "StdDev"   },   {     "value": "PctGood",     "label": "PctGood"   },   {     "value": "PctBad",     "label": "PctBad"   } ]}');

CREATE TABLE ex_lp_dashboard_widgets (
  id integer PRIMARY KEY AUTOINCREMENT,
  dashboard_id integer NOT NULL,
  widget_id integer NOT NULL,
  name text NOT NULL,
  position text NOT NULL,
  FOREIGN KEY (dashboard_id) REFERENCES ex_lp_dashboards (id) ON DELETE CASCADE,
  FOREIGN KEY (widget_id) REFERENCES ex_lp_widgets (id)
);
INSERT INTO ex_lp_dashboard_widgets VALUES(22,1,10,'Production vs Expected','1,15,8,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(23,1,4,'Hourly Case Analysis','1,13,20,27');
INSERT INTO ex_lp_dashboard_widgets VALUES(24,1,7,'Notepad','1,6,1,8');
INSERT INTO ex_lp_dashboard_widgets VALUES(25,1,5,'Daily Production','6,11,1,8');
INSERT INTO ex_lp_dashboard_widgets VALUES(26,1,9,'Progress KPI','13,27,20,27');
INSERT INTO ex_lp_dashboard_widgets VALUES(27,1,3,'Energy Yesterday','15,21,8,11');
INSERT INTO ex_lp_dashboard_widgets VALUES(28,1,3,'Real Power','15,21,11,14');
INSERT INTO ex_lp_dashboard_widgets VALUES(29,1,3,'Setpoint','15,21,14,17');
INSERT INTO ex_lp_dashboard_widgets VALUES(30,1,3,'Reactive','15,21,17,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(31,1,3,'PoaIrradiance','21,27,8,11');
INSERT INTO ex_lp_dashboard_widgets VALUES(32,1,3,'LmpPrice','21,27,11,14');
INSERT INTO ex_lp_dashboard_widgets VALUES(33,1,3,'PerformanceMtd','21,27,14,17');
INSERT INTO ex_lp_dashboard_widgets VALUES(34,1,3,'Power Factor','21,27,17,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(35,1,4,'Line 1 Prod Rate','11,20,1,8');
INSERT INTO ex_lp_dashboard_widgets VALUES(36,1,1,'Simple Gauge Battery','20,27,5,8');
INSERT INTO ex_lp_dashboard_widgets VALUES(37,1,6,'Moving Analog Indicator Coil Temp','20,25,1,5');
INSERT INTO ex_lp_dashboard_widgets VALUES(38,2,4,'Line 1 Battery vs Prod','1,14,1,10');
INSERT INTO ex_lp_dashboard_widgets VALUES(39,2,2,'L1 Oil Press','14,19,1,4');
INSERT INTO ex_lp_dashboard_widgets VALUES(40,2,2,'L1 Coil Temp','14,19,4,7');
INSERT INTO ex_lp_dashboard_widgets VALUES(41,2,2,'L1 Prod Rate','14,19,7,10');
INSERT INTO ex_lp_dashboard_widgets VALUES(42,2,2,'L1 Battery','19,24,1,4');
INSERT INTO ex_lp_dashboard_widgets VALUES(43,2,2,'L1 Reserve Oil Press','19,24,4,7');
INSERT INTO ex_lp_dashboard_widgets VALUES(44,2,2,'L1 Reserve 2 Press','19,24,7,10');
INSERT INTO ex_lp_dashboard_widgets VALUES(45,2,5,'Daily Production L1','24,30,1,10');
INSERT INTO ex_lp_dashboard_widgets VALUES(46,2,4,'Line 2 Battery vs Prod','1,14,11,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(47,2,2,'Line2 Oil Press','14,19,11,14');
INSERT INTO ex_lp_dashboard_widgets VALUES(48,2,2,'Line2 Coil Temp','14,19,14,17');
INSERT INTO ex_lp_dashboard_widgets VALUES(49,2,2,'L2 Prod Rate','14,19,17,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(50,2,2,'Line2 Battery','19,24,11,14');
INSERT INTO ex_lp_dashboard_widgets VALUES(51,2,2,'Line 2 Oil Press','19,24,14,17');
INSERT INTO ex_lp_dashboard_widgets VALUES(52,2,2,'Line2 Reserve 2 Press','19,24,17,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(53,2,5,'Daily Production Line2','24,30,11,20');
INSERT INTO ex_lp_dashboard_widgets VALUES(54,2,4,'Line 3 Battery vs Prod','1,14,21,30');
INSERT INTO ex_lp_dashboard_widgets VALUES(55,2,2,'Line3 Oil Press','14,19,21,24');
INSERT INTO ex_lp_dashboard_widgets VALUES(56,2,2,'Line3 Coil Temp','14,19,24,27');
INSERT INTO ex_lp_dashboard_widgets VALUES(57,2,2,'Line3 Prod Rate','14,19,27,30');
INSERT INTO ex_lp_dashboard_widgets VALUES(58,2,2,'Line3 Battery Capacity','19,24,21,24');
INSERT INTO ex_lp_dashboard_widgets VALUES(59,2,2,'Line 3 Oil Press','19,24,24,27');
INSERT INTO ex_lp_dashboard_widgets VALUES(60,2,2,'Line3 Reserve 2 Press','19,24,27,30');
INSERT INTO ex_lp_dashboard_widgets VALUES(61,2,5,'Daily Production Line3','24,30,21,30');
INSERT INTO ex_lp_dashboard_widgets VALUES(62,1,8,'Progress Bar Oil Press L1','25,27,1,5');

CREATE TABLE ex_lp_dashboard_widget_parameters (
  id integer PRIMARY KEY AUTOINCREMENT,
  dashboard_widget_id integer NOT NULL,
  parameter_id integer NOT NULL,
  parameter_value text,
  FOREIGN KEY (dashboard_widget_id) REFERENCES ex_lp_dashboard_widgets (id) ON DELETE CASCADE,
  FOREIGN KEY (parameter_id) REFERENCES ex_lp_widget_parameters (id) ON DELETE CASCADE
);
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(26,22,12,'{HIST}dailyproduction');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(27,22,13,'{HIST}dailyproductionexpected');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(77,22,16,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(28,23,4,'{HIST}dailyproduction');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(29,23,5,'{HIST}dailyproductionexpected');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(30,23,6,'Hourly Case Analysis');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(78,23,15,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(31,24,9,'[Launchpad]KPI/Notepad');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(32,25,7,'[Launchpad]KPI/DailyProduction');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(33,26,11,'[Launchpad]KPI/Lines');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(34,27,3,'{HIST}ambienttemperature');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(79,27,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(35,28,3,'{HIST}ambienthumidity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(80,28,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(36,29,3,'{HIST}workinprocess');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(81,29,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(37,30,3,'{HIST}buffer');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(82,30,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(38,31,3,'{HIST}cycletime');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(83,31,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(39,32,3,'{HIST}setuptime');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(84,32,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(40,33,3,'{HIST}airpressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(85,33,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(41,34,3,'{HIST}energyyesterday');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(86,34,14,'Average');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(42,35,4,'{HIST}lines/line1/productionrate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(43,35,5,'');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(44,35,6,'Line 1 Prod Rate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(87,35,15,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(45,36,1,'[Launchpad]KPI/Lines/Line1/BatteryCapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(46,37,8,'[Launchpad]KPI/Lines/Line1/CoilTemperature');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(47,38,4,'{HIST}lines/line1/batterycapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(48,38,5,'{HIST}lines/line1/productionrate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(49,38,6,'Line 1 Battery vs Prod Rate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(88,38,15,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(50,39,2,'[Launchpad]KPI/Lines/Line1/OilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(51,40,2,'[Launchpad]KPI/Lines/Line1/CoilTemperature');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(52,41,2,'[Launchpad]KPI/Lines/Line1/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(53,42,2,'[Launchpad]KPI/Lines/Line1/BatteryCapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(54,43,2,'[Launchpad]KPI/Lines/Line1/ReserveOilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(55,44,2,'[Launchpad]KPI/Lines/Line1/Reserve2Pressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(56,45,7,'[Launchpad]KPI/Lines/Line1/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(57,46,4,'{HIST}lines/line2/batterycapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(58,46,5,'{HIST}lines/line2/productionrate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(59,46,6,'Line 2 Battery vs Prod Rate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(89,46,15,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(60,47,2,'[Launchpad]KPI/Lines/Line2/OilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(61,48,2,'[Launchpad]KPI/Lines/Line2/CoilTemperature');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(62,49,2,'[Launchpad]KPI/Lines/Line2/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(63,50,2,'[Launchpad]KPI/Lines/Line2/BatteryCapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(64,51,2,'[Launchpad]KPI/Lines/Line2/ReserveOilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(65,52,2,'[Launchpad]KPI/Lines/Line2/Reserve2Pressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(66,53,7,'[Launchpad]KPI/Lines/Line2/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(67,54,4,'{HIST}lines/line3/batterycapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(68,54,5,'{HIST}lines/line3/productionrate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(69,54,6,'Line 3 Battery vs Prod Rate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(90,54,15,'Maximum');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(70,55,2,'[Launchpad]KPI/Lines/Line3/OilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(71,56,2,'[Launchpad]KPI/Lines/Line3/CoilTemperature');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(72,57,2,'[Launchpad]KPI/Lines/Line3/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(73,58,2,'[Launchpad]KPI/Lines/Line3/BatteryCapacity');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(74,59,2,'[Launchpad]KPI/Lines/Line3/OilPressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(75,60,2,'[Launchpad]KPI/Lines/Line3/Reserve2Pressure');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(76,61,7,'[Launchpad]KPI/Lines/Line3/ProductionRate');
INSERT INTO ex_lp_dashboard_widget_parameters VALUES(91,62,10,'[Launchpad]KPI/Lines/Line1/OilPressure');

CREATE TABLE ex_lp_dashboards (
  id integer PRIMARY KEY AUTOINCREMENT,
  name text NOT NULL,
  icon text DEFAULT NULL,
  url text NOT NULL,
  username text DEFAULT NULL,
  grid text NOT NULL DEFAULT 'fixed',
  cell_size integer NOT NULL DEFAULT 100,
  grid_rows integer NOT NULL DEFAULT 10,
  row_gutter_size integer NOT NULL DEFAULT 6,
  grid_cols integer NOT NULL DEFAULT 10,
  col_gutter_size integer NOT NULL DEFAULT 6,
  last_modified integer NOT NULL
);
INSERT INTO ex_lp_dashboards VALUES(1,'Dashboard 1','dashboard','dash1','Anonymous','stretch',100,26,12,26,12,'2025-06-05 20:40:13');
INSERT INTO ex_lp_dashboards VALUES(2,'Dashboard 2','dashboard','dash2','Anonymous','stretch',100,29,6,29,6,'2025-06-05 20:45:49');
"""
	# History paths must reference THIS gateway: histprov 'launchpad', driver = local system name.
	sysName = system.tag.readBlocking(["[System]Gateway/SystemName"])[0].value.lower()
	query = query.replace("{HIST}", "histprov:launchpad:/drv:%s:launchpad:/tag:kpi/" % sysName)
	system.db.runUpdateQuery(query, database=DATABASE_NAME)