task.run(".helper/create_bd", self.configuration)
task.run(".helper/create_epg", self.configuration)
task.run(".helper/addto_vlanpool", self.configuration)
task.run(".helper/create_aaep", self.configuration)

if trunk_aep:
    task.run(".helper/addto_trunk_aep", self.configuration)
