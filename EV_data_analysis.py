import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class EV():
    
    excess = None
    deficit = None

    g = 9.8066 # gravity (m/s)
    theta = 0 # road grade

    EV_model = None
    m_kg = None # mass (kg)

    #rolling resistance parameters
    C_r = None
    c_1 = None
    c_2 = None

    rho_air = None # air mass density (kg/m3)
    A_f = None # frontal area of the vehicle (m2)
    C_D = None # aerodynamic drag coefficient of the vehicle
    n_driveline = None # driveline efficiency
    n_electric_motor = None # electric motor efficiency (85%-95% for Nissan Leaf)

    capacity = 20000 #In Wh
    charge_lvl = 10000 #In Wh
    soc = (charge_lvl/capacity) * 100 #State of charge of the battery in %

    data = None

    def __init__(self):
        """
        Initialised parameters for selected EV

        :param data: -
        :return: initialised parameters
        """
        EV = self.EV_menu()

        self.EV_model = EV['vehicle_model']
        self.m = EV['m_kg']
        self.C_r = EV['C_r']
        self.c_1 = EV['c_1']
        self.c_2 = EV['c_2']
        self.rho_air = EV['rho_air']
        self.A_f = EV['A_f']
        self.C_D = EV['C_D']
        self.n_driveline = EV['n_driveline']
        self.n_electric_motor = EV['n_electric_motor']
        self.capacity = EV['capacity']
        self.charge_lvl = self.capacity * (50/100) #battery is 50% charged initially

    def charge(self,power): 
        """
        Method to charge EV battery

        :param data: power (because data is measured every second)
        :return: new SOC for the EV object
        """

        if (self.capacity-self.charge_lvl) >= power:
            self.charge_lvl += power
        else:
            temp = self.charge_lvl+power-self.capacity
            self.excess += temp
            print('Battery is full, {} Wh of excess energy'.format(temp))
            self.charge_lvl = self.capacity

    def discharge(self,power): 
        """
        Method to discharge EV battery

        :param data: power (because data is measured every second)
        :return: new SOC for the EV object
        """

        if self.charge_lvl == 0:
            self.deficit += power
            print('Battery is COMPLETELY drained, {} Wh of energy deficit'.format(power))
        elif power > self.charge_lvl:
            temp = power-self.charge_lvl
            self.deficit += temp
            print('Battery is COMPLETELY drained, {} Wh of energy deficit'.format(temp))
            self.charge_lvl = 0
        else:
            self.charge_lvl -= power


    def load_csv_data(self, file_name, subdir=''):
        """
        Loads data from .csv file in to DataFrame

        :param file_name: .csv file name in string
        :param subdir: optional parameter to specify the subdirectory of the file
        :return: extracted data in DataFrame
        """

        file_dir = os.path.realpath('./')
        for root, dirs, files in os.walk(file_dir):
            if root.endswith(subdir):
                for name in files:
                    if name == file_name:
                        file_path = os.path.join(root, name)

        df = pd.read_csv(file_path)

        return df

    def EV_menu(self):
        """
        Menu for selection of EV to be used in system

        :param data: -
        :return: dataframe containing parameters for selected EV
        """

        file = 'EV_characteristics.csv'
        EV_selection = self.load_csv_data(file)
        choice = -1
        while (choice < 0) or (choice >= len(EV_selection)):
            print('****** EV SELECTION MENU ******')
            print(EV_selection['vehicle_model'])
            choice = int(input("""Please key in the number corresponding to the vehicle model : """))
        EV = EV_selection.iloc[choice]

        return EV

    def calculate_energy_consumption(self, data):
        """
        Calculates the energy consumption trend and plots it against time

        :param data: data in DataFrame
        :return: data in DataFrame with 4 new columns: speed in m/s, acceleration in m/s^2,
                                                        power at wheels in W and power at electric motor in W
        """
        mph_to_mps = 0.44704

        self.data = data
        self.data['speed_mps'] = mph_to_mps * self.data['speed_mph']
        self.data['accel_mps2'] = mph_to_mps * self.data['accel_meters_ps']

        # Power required at the wheels
        self.data['P_wheels'] = (self.m * self.data['accel_mps2'] \
                        + self.m * self.g * np.cos(self.theta) * self.C_r * 1e-3 * (self.c_1 * self.data['speed_mps'] + self.c_2) \
                        + 0.5 * self.rho_air * self.A_f * self.C_D * (self.data['speed_mps']**2) \
                        + self.m * self.g * np.sin(self.theta)) * self.data['speed_mps']

        # Power at electric motor 
        self.data['P_electric_motor'] = self.data['P_wheels'] / (self.n_driveline * self.n_electric_motor)

        self.regen_braking()

        return data

    def regen_braking(self):
        """
        Calculates the energy consumption (with regenerative braking efficiency included)
        trend and plots it against time

        :param data: data in DataFrame
        :return: data in DataFrame with two new columns: regenerative braking efficiency
                                                        and power at electric motor adjusted with n_rb
        """
        alpha = 0.0411

        # regenerative braking efficiency is ZERO when acceleration >= 0
        self.data['n_rb'] = (np.exp(alpha / abs(self.data['accel_mps2']) ) )**-1
        self.data['n_rb'].where(self.data['accel_mps2'] < 0, other = 0, inplace = True)

        # calculate the energy being stored back to the battery whenever the car decelerates
        self.data['P_regen'] = self.data['P_electric_motor']
        self.data['P_regen'] *= self.data['n_rb']

        # add the energy consumption when the car accelerates
        pos_energy_consumption = self.data['P_electric_motor'].copy()
        pos_energy_consumption.where(self.data['accel_mps2']>=0, other=0, inplace = True)
        self.data['P_regen'] += pos_energy_consumption

        return

    def graph_plotter(self, x='timestamp', y='P_regen', file_name='energy_consumption_with_regen.png',
                    subdir='test', date='test'):
        """
        Plots a graph according to the specified x and y, and saves it to the specified file name

        :param data: data in DataFrame
        :param x: the name of the column for the x axis
        :param y: the name(s) of the column for the y axis
        :param file_name: the file name(s) to store the plot(s)
        """
        figure_folder = 'EV_figures'
        directory = figure_folder+'/'+subdir+'/'+self.EV_model+'/'+date # directory to store the figures

        if not os.path.exists(directory):
            os.makedirs(directory)

        for col, name in zip(y, file_name):
            self.data.plot(x=x, y=col)
            plt.savefig(directory+'/'+name)


EV_object = EV()

file = '2012-05-22.csv'
subdir = '1035198_1'
data = EV_object.load_csv_data(file, subdir)

data['timestamp'] = pd.to_datetime(data['timestamp'], format='%Y-%m-%d %H:%M:%S')

sliced_data = EV_object.calculate_energy_consumption(data.loc[1:593])

y = ['P_electric_motor', 'speed_mps', 'P_regen', 'n_rb']
file_name = ['energy_consumption.png', 'speed_profile.png', 'energy_consumption_with_regen.png', 'n_rb.png']
EV_object.graph_plotter(y=y, file_name=file_name, subdir=subdir, date=file.strip('.csv'))

print(sum(sliced_data['P_regen'])) #calculate the final energy consumption, accounting for RB efficiency
print(sum(sliced_data['P_electric_motor'])) #calculate the final energy consumption, NOT accounting for RB efficiency (therefore should be smaller)
