import global_configuration as global_c
import thesis
import gym
import channel
from gym import spaces
import numpy as np
import random
import matplotlib.pyplot as plt

state_list = []
action_list = []
now_ap_association = []

# action space
# action -> 應該要是 [1 x UE_num] 的形式
# 0 : means that this UE connected to WiFi
# 1 : means that this UE connected to LiFi0
# 2 : means that this UE connected to LiFi1
# 3 : means that this UE connected to LiFi2
# 4 : means that this UE connected to LiFi3
# 5 : means that this UE connected to WiFi and LiFi0
# 6 : means that this UE connected to WiFi and LiFi1
# 7 : means that this UE connected to WiFi and LiFi2
# 8 : means that this UE connected to WiFi and LiFi3


class LAHLWNenv(gym.Env):
    def __init__(self):
        # metadata = {'render.modes':['human']}
        super(LAHLWNenv,self).__init__()
        self.currstep = 1 # current step (index)

        self.action_space = spaces.MultiDiscrete(np.array([9,9,9,9,5,5,5,5,5,5])) # SAP  0 ~ 4 , total : 5 / LA   0 ~ 8 , total : 9 , ue : LA,LA,LA,LA,SAP....
        # self.action_space = spaces.Box(low= 0, high=8,shape=(global_c.UE_num,),dtype=np.int8)
        # self.action_space = LAHLWNenv.possible_action()
        
        # self.observation_space = spaces.Box(low = 0 , high = 1e10,shape=(global_c.UE_num,4),dtype=np.float32) # UE_num x 4, entry is [Wifi SNR] [highest VLC SINR] [second VLC SINR] [associated AP]
        self.observation_space = spaces.Box(low = 0, high = 1e10, shape=(global_c.UE_num + global_c.UE_num + global_c.UE_num + global_c.RF_AP_num + global_c.VLC_AP_num,), dtype=np.float32)

    def step(self, action):
        done = False
        self.currstep += 1
        
        # 法一 : action = spaces.Box(low= 0, high=8,shape=(global_c.UE_num,),dtype=np.int8)
        # my_action = LAHLWNenv.possible_action()
        # ap_associated_matrix = thesis.Thesis.action_to_AP_association_matrix(my_action)
        # channel.Channel.updateAllvlcSINR(VLC_SINR_matrix=thesis.VLC_SINR_matrix,VLC_LOS_matrix=thesis.VLC_LOS_matrix,AP_association_matrix=ap_associated_matrix)
        # new_state = thesis.Thesis.createState(my_action)
        # state_list.append(new_state)
        # action_list.append(my_action)
        # reward = thesis.Thesis.calculateR1(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2],action=action_list[len(action_list)-1],preaction=action_list[len(action_list)-2])
        # # print("state:",new_state," reward:",reward)
        # info = {}
        # if self.currstep > 1000:
        #     done = True
        
        # 法二 : actio = spaces.MultiDiscrete(np.array([9,9,9,9,5,5,5,5,5,5]))
        ap_associated_matrix = thesis.Thesis.action_to_AP_association_matrix(action=action)
        channel.Channel.updateAllvlcSINR(VLC_SINR_matrix=thesis.VLC_SINR_matrix,VLC_LOS_matrix=thesis.VLC_LOS_matrix,AP_association_matrix=ap_associated_matrix)
        new_state = thesis.Thesis.createState(action=action)
        state_list.append(new_state)
        action_list.append(action)
        reward = thesis.Thesis.calculateR1(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2],action=action_list[len(action_list)-1],preaction=action_list[len(action_list)-2])
        # print("state:",new_state," reward:",reward)
        info = {}
        if self.currstep > 1000:
            done = True

        return new_state,reward,done,info

    def reset(self):
        state_list.clear()
        action_list.clear()
        thesis.Thesis.init()
        thesis.Thesis.allSINR()
        action = [-1 for i in range(global_c.UE_num)]
        new_state = thesis.Thesis.createState(action)
        action_list.append(action)
        state_list.append(new_state)
        return new_state
    
    @staticmethod
    def possible_action():
        action = np.array([-1 for i in range(global_c.UE_num)])
        for i in range(global_c.UE_num):
            if thesis.my_ue_list[i].group == "SAP":
                action[i] = random.randint(0,4)
            if thesis.my_ue_list[i].group == "LA":
                action[i] = random.randint(0,8)
        return action
    
    def render(self):
        print("rander!")
        self.make_room()
        
    def make_room(self):
        ue_x = []
        ue_y = []
        for i in range(global_c.UE_num):
            ue_x.append(thesis.my_ue_list[i].x_pos)
            ue_y.append(thesis.my_ue_list[i].y_pos)
        ue_color = np.array(['b' for i in range(global_c.UE_num)]) 
        
        ap_x = []
        ap_y = []
        for j in range(global_c.RF_AP_num+global_c.VLC_AP_num):
            ap_x.append(thesis.my_ap_list[j].x_pos)
            ap_y.append(thesis.my_ap_list[j].y_pos)
        ap_color = np.array(['r','g','g','g','g'])
        x = np.append(ue_x,ap_x)
        y = np.append(ue_y,ap_y)
        color = np.append(ue_color,ap_color)
        plt.ylim(-global_c.room_size/2,global_c.room_size/2)
        plt.xlim(-global_c.room_size/2,global_c.room_size/2)
        plt.scatter(x, y, c = color)
        plt.show()
        plt.close()

    def close(self):
        pass

    # def seed(self,seed = None):
    #     return


# if __name__ == '__main__':
#     env = LAHLWNenv()
#     obs = env.reset()
#     while True:
#         action = LAHLWNenv.possible_action()
#         obs,re,done,info = env.step(action=action)
#         if done:
#             # env.reset()
#             break
#     ue_demand = thesis.Thesis.getUEdemand()
#     print(ue_demand)
