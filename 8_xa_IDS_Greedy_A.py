import tkinter as tk
import random
import copy
from PIL import Image, ImageTk
from collections import deque
import heapq

class eight_xa:
    def __init__(self, root):
        self.root = root
        self.root.title("8 queen")
        self.root.config(bg="lightgray")
        self.n = 8

        #Vị trí quân xe mục tiêu cần đạt được
        self.node_goal = []
            
        self.frame_left = tk.Frame(self.root, bg="lightgray", relief="solid", borderwidth=1)
        self.frame_left.grid(row=0, column=0, padx=10, pady=5)

        self.frame_right = tk.Frame(self.root, bg="lightgray", relief="solid", borderwidth=1)
        self.frame_right.grid(row=0, column=1, padx=10, pady=5)

        frame_btn = tk.Frame(self.root, bg="lightgray")
        frame_btn.grid(row=1, column=0, columnspan=2)

        IDS_btn = tk.Button(frame_btn, text="IDS", width=10, height=2, bg="lightblue")
        Greedy_btn = tk.Button(frame_btn, text="Greedy", width=10, height=2, bg="lightblue")
        A_btn = tk.Button(frame_btn, text="A*", width=10, height=2, bg="lightblue")
        IDS_btn.grid(row=0, column=0, pady=5, padx=25)
        Greedy_btn.grid(row=0, column=1, pady=5, padx=25)
        A_btn.grid(row=0, column=2, pady=5, padx=25)
        
        self.status_label = tk.Label(self.root, text="", bg="lightgray", fg="red", font=("Arial", 14, "bold"))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.whiteX = ImageTk.PhotoImage(Image.open("./whiteX.png").resize((60, 60)))
        self.blackX = ImageTk.PhotoImage(Image.open("./blackX.png").resize((60, 60)))
        self.img_null = tk.PhotoImage(width=1, height=1)
        
        self.buttons_left = self.create_widget(self.frame_left)
        self.buttons_right = self.create_widget(self.frame_right)
        
        IDS_btn.config(command=lambda: self.run_function(self.set_xa_IDS))        
        Greedy_btn.config(command=lambda: self.run_function(self.set_xa_Greedy))
        A_btn.config(command=lambda: self.run_function(self.set_xa_Astar))
    
    #Tạo bàn cờ và vẽ quân cờ
    def create_widget(self, frame):
        buttons = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                color = "white" if (i + j) % 2 == 0 else "black"
                btn = tk.Button(frame, image=self.img_null, width=60, height=60, bg=color,
                                relief="flat", borderwidth=0, highlightthickness=0)
                btn.grid(row = i, column = j, padx=1, pady=1)
                row.append(btn)
            buttons.append(row)
        return buttons
    
    def draw_xa(self, node):
        for i, j in node:
            if (i + j) % 2 == 0:
                self.buttons_right[i][j].config(image=self.blackX)
            else:
                self.buttons_right[i][j].config(image=self.whiteX)
    
    def run_function(self, f):
        for i in range(self.n):
            for j in range(self.n):
                self.buttons_right[i][j].config(image=self.img_null)
        self.status_label.config(text="Đang chạy..")
        self.root.update_idletasks()
        f()
        self.status_label.config(text="")
    
    def check_goal(self, node):     #Kiểm tra điều kiện đạt goal: số lượng đã đủ và ko 2 quân nào khắc nhau
        if node == self.node_goal:
            return True
        return False
    
    def make_child_node(self, node, x, y, cost_her=-1, cost=-1, cost_a=-1):       #Sinh ra nhánh con child
        child = []
        child = copy.deepcopy(node)
        if cost_her == -1 and cost_a == -1:
            child.append((x, y))
        elif cost_a == -1:
            child.append((x, y, cost_her))
        else:
            child.append((x, y, cost_her, cost, cost_a))
        return child  
    
    def create_node_goal(self):
        _ = [col for col in range(self.n)]
        random.shuffle(_)
        for i in range(self.n):
            j = _.pop()
            self.node_goal.append((i, j))
    
    #Hàm đặt xe bằng IDS
    def set_xa_IDS(self):
        self.node_goal = []
        self.create_node_goal()
        for depth in range(100000):
            result = self.set_xa_DLS(depth)
            if result != "cutoff" and result != False:
                self.result_ids = result
                self.draw_xa(result)
                return result
        return None
    
    def set_xa_DLS(self, limit):
        x, y = self.node_goal[0]
        node = [(x, y)]
        return self.recursive_DLS(node, limit)
    
    def recursive_DLS(self, node, limit):
        if self.check_goal(node):
            return node
        elif limit == 0:
            return "cutoff"
        else:
            cutoff_occurred = False
            x = node[len(node) - 1][0] + 1
            for y in range(self.n):
                child = self.make_child_node(node, x, y)
                result = self.recursive_DLS(child, limit - 1)
                if result == "cutoff":
                    cutoff_occurred = True
                elif result != False:
                    return result
            if cutoff_occurred:
                return "cutoff"
            else:
                return False
    
    #Hàm đặt xe bằng Greedy
    def set_xa_Greedy(self):
        self.node_goal = []
        self.create_node_goal()
        start = (self.node_goal[0][0], self.node_goal[0][1])
        queue = []
        start_cost = self.n*2 - len(start)
        start = [start + (start_cost,)]
        heapq.heappush(queue, (start[0][2], start))         
        reach_goal = False

        while queue:
            node = heapq.heappop(queue)[1]
            node_pos = [(x, y) for (x, y, *_) in node]
            if self.check_goal(node_pos):
                reach_goal = True
                self.draw_xa(node_pos)
                return node
            
            x = node[-1][0] + 1
            if x >= 8 and not reach_goal:
                continue
            for y in range(self.n):
                cost = self.heuristic(node, x, y)
                child = self.make_child_node(node, x, y, cost)
                heapq.heappush(queue, (child[-1][2], child))
    
    def heuristic(self, node, x, y):
        set_X, set_y = {x}, {y}
        for _x, _y, *_ in node:
            set_X.add(_x)
            set_y.add(_y)
        return self.n - len(set_X) + self.n - len(set_y)            

    #Hàm đặt xe bằng A*
    def set_xa_Astar(self):
        self.node_goal = []
        self.create_node_goal()
        start = (self.node_goal[0][0], self.node_goal[0][1])
        queue = []
        start_cost_her = self.n*2 - len(start)
        start_cost = 0
        start_cost_a = start_cost_her + start_cost
        start = [start + (start_cost_her, start_cost, start_cost_a,)]
        heapq.heappush(queue, (start[0][4], start))    #(key, value)     
        reach_goal = False

        while queue:
            node = heapq.heappop(queue)[1]
            node_pos = [(x, y) for (x, y, *_) in node]
            if self.check_goal(node_pos):
                reach_goal = True
                self.draw_xa(node_pos)
                return node
            
            x = node[-1][0] + 1
            if x >= 8 and not reach_goal:
                continue
            for y in range(self.n):
                cost_her = self.heuristic(node, x, y)
                cost = node[-1][3] + 1
                cost_a = cost_her + cost
                child = self.make_child_node(node, x, y, cost_her, cost, cost_a)
                heapq.heappush(queue, (child[-1][4], child))
        pass
    
if __name__ == "__main__":
    root = tk.Tk()
    game = eight_xa(root)
    root.mainloop()