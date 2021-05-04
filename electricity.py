import numpy as np


class User:
    def __init__(self, h: int, a: int, w: list = None, x_user: list = None, x_sch: list = None, s_user: list = None,
                 t_sch: list = None) -> None:
        """
        :param h: Total number of hours a day
        :param a: Total number of the user's appliance
        :param w: Coefficient of preference
        :param x_user: Electricity consumption of the user
        :param x_sch: Scheduled electricity consumption of the user
        :param s_user: Storage consumption of the user
        """
        self.price = 1
        self.time = 0
        self.num_appliance = a
        if w is None:
            self.w = np.random.random(a)
        else:
            self.w = w
        if x_user is None:
            self.x_user = np.random.random((h, a)) * 10
        else:
            self.x_user = x_user
        if x_sch is None:
            self.x_sch = np.zeros((h, a))
        else:
            self.x_sch = x_sch
        if s_user is None:
            self.s_user = np.random.random(h)
        else:
            self.s_user = s_user
        if t_sch is None:
            self.t_sch = np.random.randint(low=0, high=h, size=(a, 2))
            for h_ in range(h):
                for a_ in range(self.num_appliance):
                    if self.t_sch[a_][0] <= h_ <= self.t_sch[a_][1]:
                        self.x_sch[h_, a_] = np.random.random() * 10
                    elif self.t_sch[a_][0] > self.t_sch[a_][1] and (h_ >= self.t_sch[a_][0] or h_ <= self.t_sch[a_][1]):
                        self.x_sch[h_, a_] = np.random.random() * 10
        else:
            self.t_sch = t_sch
        print(self.t_sch)

    def change(self, x_user_new: float, s_user_new: float) -> None:
        """
        Change the user's strategy
        :param x_user_new: New electricity consumption
        :param s_user_new: New storage consumption
        """
        self.x_user[self.time] = x_user_new
        self.s_user[self.time] = s_user_new

    def is_unchanged(self, x_user_new: float, s_user_new: float) -> bool:
        """
        Judge if there is a change
        :param x_user_new: New electricity consumption
        :param s_user_new: New storage consumption
        :return: If there is a change
        """
        return np.all(self.x_user - epsilon <= x_user_new <= self.x_user + epsilon) and np.all(
            self.s_user - epsilon <= s_user_new <= self.s_user + epsilon)

    def is_used(self) -> list:
        """
        Judge if all appliance used at some time interval
        :return: If all appliance used at some time interval
        """
        is_use_list = np.zeros(self.num_appliance)
        for i in range(self.num_appliance):
            if self.t_sch[i][0] <= self.t_sch[i][1]:
                is_use_list[i] = self.t_sch[i][0] <= self.time <= self.t_sch[i][1]
            else:
                is_use_list[i] = self.time >= self.t_sch[i][0] or self.time <= self.t_sch[i][1]
        return is_use_list

    def charge_t(self) -> float:
        """
        Calculate the user's electric charge of time t
        :return: electric charge
        """
        return self.price * (self.x_user[self.time] + self.s_user[self.time]) \
               / (np.sum(self.x_user) + np.sum(self.s_user))

    def discomfort_t(self) -> float:
        """
        Calculate the user's discomfort of time t
        :return: discomfort
        """
        return np.sum(np.multiply(self.w, (self.x_user[self.time] - self.x_sch[self.time]) ** 2))

    def sum_cost_t(self, x: list = None) -> float:
        """
        Calculate the user's total cost of time t
        :return:
        """
        if x is None:
            return self.price * (self.x_user[self.time] + self.s_user[self.time]) \
                   / (np.sum(self.x_user) + np.sum(self.s_user)) \
                   + np.sum(np.multiply(self.w, (self.x_user[self.time] - self.x_sch[self.time]) ** 2))
        else:
            return self.price * (sum(x)) / (np.sum(self.x_user) + np.sum(self.s_user)) \
                   + np.sum(np.multiply(self.w, (x[:-1] - self.x_sch[self.time]) ** 2))


class Electricity:
    def __init__(self, n: int, h: int, e_sch=None, l=None):
        """
        :param n: Number of users
        :param l: List of users
        """
        self.time = np.arange(h).__iter__()
        self.t = 0
        if l is None:
            self.user_list = [User(h, np.random.randint(3, 7)) for _ in range(n)]
        else:
            self.user_list = l
        if e_sch is None:
            self.e_sch = np.random.randint(low=0, high=h, size=2)
        else:
            self.e_sch = e_sch
        print(self.e_sch)

    def set_time(self):
        self.t = self.time.__next__()
        return self.t

    def is_not_power(self):
        return not self.t in range(np.min(self.e_sch), np.max(self.e_sch) + 1)

    def set_price_t(self, g):
        """
        Calculate the price of the electricity
        :return: price (P(t)=g*Lt^2)
        """
        total = 0
        for i in range(len(self.user_list)):
            total += np.sum(self.user_list[i].x_user[self.t]) + self.user_list[i].s_user[self.t]
            self.user_list[i].time = self.t
            self.user_list[i].price = g * total ** 2
        return g * total ** 2

    def reset_time(self, h):
        self.time = np.arange(h).__iter__()
