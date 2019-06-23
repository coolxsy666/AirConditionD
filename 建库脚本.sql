CREATE TABLE `server_request` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roomid` varchar(45) NOT NULL,
  `temp` decimal(4,2) NOT NULL,
  `speed` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `cost` decimal(7,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=543 DEFAULT CHARSET=latin1;
CREATE TABLE `server_dailyreport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roomid` varchar(45) NOT NULL,
  `time` datetime NOT NULL,
  `use_times` int(11) NOT NULL,
  `fre_temp` decimal(4,2) NOT NULL,
  `fre_speed` int(11) NOT NULL,
  `dispatch_times` int(11) NOT NULL,
  `details_times` int(11) NOT NULL,
  `sumcost` decimal(7,2) NOT NULL,
  `change_speed_times` int(11) NOT NULL,
  `change_temp_times` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=357 DEFAULT CHARSET=latin1;
CREATE TABLE `server_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roomid` varchar(45) NOT NULL,
  `tar_temp` decimal(4,2) NOT NULL,
  `cur_temp` decimal(4,2) NOT NULL,
  `speed` int(11) NOT NULL,
  `cost` decimal(7,2) NOT NULL,
  `state` int(11) NOT NULL,
  `serve_time` int(11) NOT NULL,
  `wait_time` int(11) NOT NULL,
  `energy` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=latin1;