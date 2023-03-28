import global_configuration as global_c
import thesis
import gym
import channel
from gym import spaces
import numpy as np
import random
state_list = []
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
        # self.action_space = spaces.Discrete(10) # 10 possible APS ( 0 ~ 9 )
        # self.observation_space = spaces.Box(low = 0 , high = 1e10,shape=(global_c.UE_num,4),dtype=np.float32) # UE_num x 4, entry is [Wifi SNR] [highest VLC SINR] [second VLC SINR] [associated AP]
    
    def step(self, action):
        done = False
        self.currstep += 1
        ap_associated_matrix = thesis.Thesis.action_to_AP_association_matrix(action)
        channel.Channel.updateAllvlcSINR(VLC_SINR_matrix=thesis.VLC_SINR_matrix,VLC_LOS_matrix=thesis.VLC_LOS_matrix,AP_association_matrix=ap_associated_matrix)
        new_state = thesis.Thesis.createState(action)
        state_list.append(new_state)
        reward = thesis.Thesis.calculateR1(state=state_list[len(state_list)-1],prestate=state_list[len(state_list)-2])
        print("step:",self.currstep," reward:",reward)
        info = {}
        if self.currstep > 1000:
            done = True
        return new_state,reward,done,info

    def reset(self):
        thesis.Thesis.init()
        thesis.Thesis.allSINR()
        action = [-1 for i in range(global_c.UE_num)]
        new_state = thesis.Thesis.createState(action)
        state_list.append(new_state)
        return new_state
    
    @staticmethod
    def possible_action():
        action = [-1 for i in range(global_c.UE_num)]
        for i in range(global_c.UE_num):
            if thesis.my_ue_list[i].group == "SAP":
                action[i] = random.randint(0,4)
            if thesis.my_ue_list[i].group == "LA":
                action[i] = random.randint(0,8)
        print(action)
        return action
    
    def render(self):
        print("step:",self.currstep)
    
    def close(self):
        pass

    # def seed(self,seed = None):
    #     return


if __name__ == '__main__':
    env = LAHLWNenv()
    obs = env.reset()
    while True:
        action = LAHLWNenv.possible_action()
        obs,re,done,info = env.step(action=action)
        if done:
            # env.reset()
            break