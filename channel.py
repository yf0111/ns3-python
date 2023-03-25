import global_configuration as global_c
import math


class Channel:
    def __init__(self):
        pass
    
    # vlc channel gain
    @staticmethod
    def radianDegree(radian):
        return radian * 180.0 / global_c.PI
    
    @staticmethod
    def getCosineOfIncidenceAngle(ue,ap):
        polar_angle = ue.polar_angle
        azimuth_angle = ue.azimuth_angle
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        dz = ap.z_pos - ue.z_pos
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        first_term = dx * math.sin(polar_angle) * math.cos(azimuth_angle)
        second_term = dy * math.sin(polar_angle) * math.sin(azimuth_angle)
        last_term = dz * math.cos(polar_angle)
        return (first_term + second_term + last_term) / dist
    
    @staticmethod
    def getIrradianceAngle(ue,ap):
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        plane_dist = math.sqrt(dx*dx + dy*dy)
        height_diff = ap.z_pos - ue.z_pos
        return math.atan(plane_dist / height_diff)
    
    @staticmethod
    def getDistance(ue,ap):
        dx = ap.x_pos - ue.x_pos
        dy = ap.y_pos - ue.y_pos
        dz = ap.z_pos - ue.z_pos
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    @staticmethod
    def estimateOneVlcLightOfSight(ue,ap):
        cosine_incidence_angle = Channel.getCosineOfIncidenceAngle(ue,ap)
        if Channel.radianDegree(math.acos(cosine_incidence_angle)) > global_c.field_of_view / 2 :
            return 0.0
        irradiance_angle = Channel.getIrradianceAngle(ue=ue,ap=ap)
        distance = Channel.getDistance(ue=ue,ap=ap)
        los = (global_c.lambertian_coefficient + 1) * global_c.receiver_area / (2 * global_c.PI * math.pow(distance,2))
        los = los * math.pow(math.cos(irradiance_angle),global_c.lambertian_coefficient)
        los = los * cosine_incidence_angle
        los = los * global_c.concentrator_gain
        los = los * global_c.filter_gain
        return los

    @staticmethod
    def calculateAllVlcLightOfSight(my_ue_list,VLC_LOS_matrix,my_ap_list):
        for i in range (global_c.UE_num):
            my_ue_list[i].randomOrientationAngle()
        for AP_index in range(global_c.VLC_AP_num):   
            for UE_index in range (global_c.UE_num):
                VLC_LOS_matrix[AP_index][UE_index] = Channel.estimateOneVlcLightOfSight(my_ue_list[UE_index],my_ap_list[AP_index])
    
    # vlc sinr
    @staticmethod
    def calculateAllVlcSINR(VLC_LOS_matrix,VLC_SINR_matrix,my_ue_list,my_ap_list):
        for AP_index in range (global_c.VLC_AP_num):
            for UE_index in range (global_c.UE_num):
                VLC_SINR_matrix = Channel.estimateOneVlcSINR(VLC_LOS_matrix=VLC_LOS_matrix,ue=my_ue_list[UE_index],ap=my_ap_list[AP_index])
    
    @staticmethod
    def estimateOneVlcSINR(VLC_LOS_matrix,ue,ap):
        interference = 0.0
        for AP_index in range(global_c.VLC_AP_num):
            if AP_index != ap:
                interference += math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[AP_index][ue],2)
        noise = global_c.VLC_AP_bandwidth * global_c.VLC_noise_power_spectral_density
        SINR = math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[ap][ue],2) / (interference + noise)
        return SINR
    
    @staticmethod
    def updateAllvlcSINR(VLC_LOS_matrix,VLC_SINR_matrix,AP_association_matrix):
        for VLC_AP_index in range(global_c.VLC_AP_num):
            for UE_index in range(global_c.UE_num):
                VLC_SINR_matrix = Channel.estimateUpdateVlcSINR(VLC_LOS_matrix,VLC_AP_index,UE_index,AP_association_matrix)

    @staticmethod
    def estimateUpdateVlcSINR(VLC_LOS_matrix,VLC_AP_index,UE_index,AP_association_matrix):
        i_flag = 0
        for check in range(global_c.UE_num):
            if check != UE_index and AP_association_matrix[VLC_AP_index][check] == 1 :
                i_flag = 1
        interference = 0.0
        if i_flag == 1 :
            for AP_index in range(global_c.VLC_AP_num):
                if AP_index != VLC_AP_index:
                    interference += math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[AP_index][UE_index],2)
        noise = global_c.VLC_AP_bandwidth * global_c.VLC_noise_power_spectral_density
        SINR = math.pow(global_c.conversion_efficiency * global_c.VLC_AP_power * VLC_LOS_matrix[VLC_AP_index][UE_index],2) / (interference + noise)
    
    @staticmethod
    def calculateAllVlcDataRate(VLC_SINR_matrix,VLC_data_rate_matrix):
        for AP_index in range(global_c.VLC_AP_num):
            for UE_index in range(global_c.UE_num):
                VLC_data_rate_matrix[AP_index][UE_index] = Channel.estimateOneVlcDataRate(VLC_SINR_matrix,AP_index,UE_index)
    
    @staticmethod
    def estimateOneVlcDataRate(VLC_SINR_matrix,AP_index,UE_index):
        data_rate = (global_c.VLC_AP_bandwidth / 2) * math.log2(1 + (6 / math.pi * math.e)) * VLC_SINR_matrix[AP_index][UE_index]
        return 0.0 if math.isnan(data_rate) else data_rate
    
    
        