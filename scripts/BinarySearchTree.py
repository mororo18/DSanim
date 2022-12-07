from manim import *

class Node:
    def __init__(self, item, left, right, depth):
        self.item = item
        self.left = left
        self.right = right
        self.depth = depth

    def get_depth(self):
        return self.depth

    def get_item(self):
        return self.item
    def set_item(self, item):
        self.item = item


    def set_left(self, node):
        self.left = node
    def set_right(self, node):
        self.right = node

    def get_left(self):
        return self.left
    def get_right(self):
        return self.right

class BinarySearchTree(MovingCameraScene):
    def print(self, text):
        prompt=Text(text).move_to(self.camera.frame_center).scale(self.camera.frame_width / self.O_WIDTH).set_color(BLACK)
        box = Rectangle(width=prompt.width*1.1 , height = prompt.height + prompt.width*0.1).move_to(self.camera.frame_center).set_color(BLACK)
        box.set_fill(WHITE, 0.8)

        label = VGroup(box, prompt)

        self.play(FadeIn(label), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(label), run_time=0.5)

    def search(self, item):
        if self.root == None:
            self.print("Árvore vazia.")
            return False
        ret =  self.rsearch(self.root, item)

        if ret == True:
            self.print("Item {} encontrado.".format(item))
        else:
            self.print("Item {} não encontrado.".format(item))

        self.play(
            self.tudo.animate.set_color(color=WHITE, family=True), run_time=0.5
                )

        return ret

    def rsearch(self, node, item):
        vitem = self.get_vitem(node.get_item())
        vnode = self.get_vnode(node.get_item())
        node_item = int(vitem.original_text)
        if node_item == item:
            self.play(
                vnode.animate.set_color(color=GREEN, family=True)
                    )

            return True

        if item < node_item and node.get_left() != None:
            self.play(
                vnode.animate.set_color(color=RED, family=True)
                    )
            return self.rsearch(node.get_left(), item)

        if item > node_item and node.get_right() != None:
            self.play(
                vnode.animate.set_color(color=RED, family=True)
                    )
            return self.rsearch(node.get_right(), item)

        return False

    def element_width(self, depth):
        return self.max_width / (2**depth)

    def right_son_pos(self, center, depth):
        pai_width = self.element_width(depth)
        pai_width /= 2
        return center + (DOWN*self.E_HEIGHT + RIGHT*pai_width)

    def left_son_pos(self, center, depth):
        pai_width = self.element_width(depth) 
        pai_width /= 2
        return center + (DOWN*self.E_HEIGHT + LEFT*pai_width)

    def build_left_arrow(self, circle_center, depth):
        start = circle_center
        end =  self.left_son_pos(circle_center, depth)
        arrow = Arrow(start=start, end=end)

        dist = arrow.get_length() - 2

        d_radius = (end - start) / arrow.get_length()
        n_start = circle_center + d_radius*0.9
        n_end = n_start + d_radius * dist
        arrow.put_start_and_end_on(start=n_start,  end=n_end)

        return arrow

    def build_right_arrow(self, circle_center, depth):
        start = circle_center
        end =  self.right_son_pos(circle_center, depth)
        arrow = Arrow(start=start, end=end)

        dist = arrow.get_length() - 2

        d_radius = (end - start) / arrow.get_length()
        n_start = circle_center + d_radius*0.9
        n_end = n_start + d_radius * dist
        arrow.put_start_and_end_on(start=n_start,  end=n_end)
        return arrow

    def move_left_arrow(self, arrow, circle_center, depth):
        start = circle_center
        end =  self.left_son_pos(circle_center, depth)
        narrow = Arrow(start=start, end=end)

        dist = narrow.get_length() - 2

        d_radius = (end - start) / narrow.get_length()
        n_start = circle_center + d_radius*0.9
        n_end = n_start + d_radius * dist
        arrow.put_start_and_end_on(start=n_start,  end=n_end)

    def move_right_arrow(self, arrow, circle_center, depth):
        start = circle_center
        end =  self.right_son_pos(circle_center, depth)
        narrow = Arrow(start=start, end=end)

        dist = narrow.get_length() - 2

        d_radius = (end - start) / narrow.get_length()
        n_start = circle_center + d_radius*0.9
        n_end = n_start + d_radius * dist
        arrow.put_start_and_end_on(start=n_start,  end=n_end)

    def set_right_arrow(self, e, arrow):
        e[-1] = arrow
    def set_left_arrow(self, e, arrow):
        e[-2] = arrow


    def get_circle(self, e):
        return e[0]
    def get_vitem(self, e):
        return e[1]
    def get_vnode(self, e):
        return e[:2]
    def get_arrows(self, e):
        return e[:-2]
    def get_right_arrow(self, e):
        return e[-1]
    def get_left_arrow(self, e):
        return e[-2]

    def insert(self, item):
        if self.root == None:
            circle = Circle(color=WHITE)
            item = Text("{}".format(item)).move_to(circle.get_center())
            l_arrow = self.build_left_arrow(circle.get_center(), 0)
            r_arrow = self.build_right_arrow(circle.get_center(), 0)
            group = VGroup(circle, item, l_arrow, r_arrow)
            self.tudo += self.get_vnode(group)

            self.root = Node(group, None, None, 0)

            v_root = self.root.get_item()
            self.play(FadeIn(self.get_vnode(v_root)))
            #self.play(FadeIn(self.get_vnode(v_root)))
        else:
            self.rinsert(self.root, item)

            self.play(
                    self.tudo.animate.set_color(color=WHITE, family=True), run_time=0.4
                    )

    def build_element_left(self, item, pai_element, depth):
        v_node_pai = self.get_vnode(pai_element)
        circle = Circle(color=WHITE).move_to(self.left_son_pos(v_node_pai.get_center(), depth))
        item = Text("{}".format(item)).move_to(circle.get_center())
        l_arrow = self.build_left_arrow(circle.get_center(), depth+1)
        r_arrow = self.build_right_arrow(circle.get_center(),depth+1)
        return VGroup(circle, item, l_arrow, r_arrow)

    def build_element_right(self, item, pai_element, depth):
        v_node_pai = self.get_vnode(pai_element)
        circle = Circle(color=WHITE).move_to(self.right_son_pos(v_node_pai.get_center(), depth))
        item = Text("{}".format(item)).move_to(circle.get_center())
        l_arrow = self.build_left_arrow(circle.get_center(), depth+1)
        r_arrow = self.build_right_arrow(circle.get_center(), depth+1)
        return VGroup(circle, item, l_arrow, r_arrow)

    def update_max_depth_width(self, node):
        if node.get_depth()+1 > self.max_depth:
            self.max_depth = node.get_depth()+1
            self.max_width = (2**self.max_depth) * self.MIN_E_WIDTH

    def rreposit(self, node_pai):


        pai_depth = node_pai.get_depth()
        pai_element = node_pai.get_item()
        pai_vnode = self.get_vnode(pai_element)
        pai_center = pai_vnode.get_center()
        pai_larrow = self.get_left_arrow(pai_element)
        pai_rarrow = self.get_right_arrow(pai_element)

        left_pos = self.left_son_pos(pai_center, pai_depth)
        right_pos = self.right_son_pos(pai_center, pai_depth)

        # esquerda
        if node_pai.get_left() != None:
            node_son_left = node_pai.get_left()

            # originais
            left_element = node_son_left.get_item()
            left_vnode = self.get_vnode(left_element)

            left_rarrow = self.get_right_arrow(left_element)
            left_larrow = self.get_left_arrow( left_element)


            #copias e alteracoes
            left_element_cpy = node_son_left.get_item().copy()
            left_vnode_cpy = self.get_vnode(left_element_cpy)

            left_vnode_cpy.move_to(left_pos)
            left_center_new = left_vnode_cpy.get_center()

            left_rarrow_cpy = self.get_right_arrow(left_element_cpy)
            left_larrow_cpy = self.get_left_arrow(left_element_cpy)

            self.move_right_arrow(left_rarrow_cpy, left_center_new,pai_depth+1)
            self.move_left_arrow(left_larrow_cpy,  left_center_new,pai_depth+1)


            # add aos grupos
            self.tudo_B += left_vnode
            self.tudo_A += left_vnode_cpy

            if node_son_left.get_left() != None:
                self.tudo_B += left_larrow
                self.tudo_A += left_larrow_cpy
            else:
                self.set_left_arrow(left_element, left_larrow_cpy)

            if node_son_left.get_right() != None:
                self.tudo_B += left_rarrow
                self.tudo_A += left_rarrow_cpy
            else:
                self.set_right_arrow(left_element, left_rarrow_cpy)


            node_new = Node(left_element_cpy, node_son_left.get_left(), node_son_left.get_right(), node_son_left.get_depth())
            self.rreposit(node_new)
            #self.rreposit(node_son_left)

        # direita
        if node_pai.get_right() != None:
            node_son_right = node_pai.get_right()

            # originais
            right_element = node_son_right.get_item()
            right_vnode = self.get_vnode(right_element)

            right_rarrow = self.get_right_arrow(right_element)
            right_larrow = self.get_left_arrow( right_element)

            # copias e as alteracoes
            right_element_cpy = node_son_right.get_item().copy()
            right_vnode_cpy = self.get_vnode(right_element_cpy)

            right_vnode_cpy.move_to(right_pos)
            right_center_new = right_vnode_cpy.get_center()

            right_rarrow_cpy = self.get_right_arrow(right_element_cpy)
            right_larrow_cpy = self.get_left_arrow( right_element_cpy)

            self.move_right_arrow(right_rarrow_cpy, right_center_new, pai_depth+1)
            self.move_left_arrow(right_larrow_cpy, right_center_new, pai_depth+1)

            # add aos grupos
            self.tudo_B += right_vnode
            self.tudo_A += right_vnode_cpy

            if node_son_right.get_left() != None:
                self.tudo_B += right_larrow
                self.tudo_A += right_larrow_cpy
            else:
                self.set_left_arrow(right_element, right_larrow_cpy)

            if node_son_right.get_right() != None:
                self.tudo_B += right_rarrow
                self.tudo_A += right_rarrow_cpy
            else:
                self.set_right_arrow(right_element, right_rarrow_cpy)


            #right_rarrow = self.build_right_arrow(right_center_new, pai_depth+1)
            #right_larrow = self.build_left_arrow(right_center_new, pai_depth+1)

            #self.set_left_arrow(right_element, right_larrow)
            #self.set_right_arrow(right_element, right_rarrow)

            node_new = Node(right_element_cpy, node_son_right.get_left(), node_son_right.get_right(), node_son_right.get_depth())
            self.rreposit(node_new)
            #self.rreposit(node_son_right)




    def reposition(self, crnt_depth):
        if crnt_depth > self.max_depth:
            self.max_depth = crnt_depth
            self.max_width = (2**self.max_depth) * self.MIN_E_WIDTH * 0.9

            print("Max depth ", self.max_depth)
            self.tudo_A = VGroup()
            self.tudo_B = VGroup()

            # originais
            root_element = self.root.get_item()
            root_vnode = self.get_vnode(root_element)

            root_rarrow = self.get_right_arrow(root_element)
            root_larrow = self.get_left_arrow(root_element)


            # copias e mods
            root_element_cpy = self.root.get_item().copy()
            root_vnode_cpy = self.get_vnode(root_element_cpy)
            root_center = root_vnode_cpy.get_center()

            root_rarrow_cpy = self.get_right_arrow(root_element_cpy)
            root_larrow_cpy = self.get_left_arrow(root_element_cpy)

            self.move_left_arrow(root_larrow_cpy, root_center, 0)
            self.move_right_arrow(root_rarrow_cpy, root_center, 0)


            self.tudo_B += root_vnode
            self.tudo_A += root_vnode_cpy
            if self.root.get_left() != None:
                self.tudo_B += root_larrow
                self.tudo_A += root_larrow_cpy
            else:
                self.set_left_arrow(root_element, root_larrow_cpy)

            if self.root.get_right() != None:
                self.tudo_B += root_rarrow
                self.tudo_A += root_rarrow_cpy
            else:
                self.set_right_arrow(root_element, root_rarrow_cpy)


            self.rreposit(Node(self.root.get_item(), self.root.get_left(), self.root.get_right(), 0))

            if self.root.get_right() != None or self.root.get_left() != None:
                # tentativa de econi=omizar movimentos de camera
                if self.camera.frame.width < self.tudo_A.width or self.camera.frame.height < self.tudo_A.height:
                    if self.tudo_A.width < self.tudo_A.height:
                        self.play(
                            Transform(self.tudo_B, self.tudo_A),
                            self.camera.frame.animate.set(height=self.tudo_A.height * 1.5).move_to(self.tudo_A.get_center())
                                )
                    else:
                        self.play(
                            Transform(self.tudo_B, self.tudo_A),
                            self.camera.frame.animate.set(width=self.tudo_A.width * 1.5).move_to(self.tudo_A.get_center())
                                )
                else:
                    self.play(
                        Transform(self.tudo_B, self.tudo_A))

    def rinsert(self, node, item):
        element = node.get_item()

        node_item = self.get_vitem(element).original_text
        node_item = int(node_item)
        
        print(node.get_depth())
        if item < node_item:
            if node.get_left() == None:
                self.reposition(node.get_depth()+1)

                new_element = self.build_element_left(item, element, node.get_depth())
                node.set_left(Node(new_element, None, None, node.get_depth()+1))

                pai_larrow = self.get_left_arrow(element)

                self.tudo += self.get_vnode(new_element)
                self.tudo += pai_larrow
                
                if self.tudo.width < self.tudo.height:
                    self.play(
                        FadeIn(self.get_vnode(new_element)),
                        GrowArrow(pai_larrow),
                        self.camera.frame.animate.set(height=self.tudo.height * 1.5).move_to(self.tudo.get_center())
                            )
                else:
                    self.play(
                        FadeIn(self.get_vnode(new_element)),
                        GrowArrow(pai_larrow),
                        self.camera.frame.animate.set(width=self.tudo.width * 1.5).move_to(self.tudo.get_center())
                            )

                return True
            else:
                l_arrow = self.get_left_arrow(element)
                l_son = self.get_vnode(node.get_left().get_item())

                self.play(
                        l_arrow.animate.set_color(color=RED),
                        l_son.animate.set_color(color=RED, family=True), run_time=0.8
                        )
                return self.rinsert(node.get_left(), item)

        if item > node_item:
            if node.get_right() == None:
                self.reposition(node.get_depth()+1)
                
                new_element = self.build_element_right(item, element, node.get_depth())
                node.set_right(Node(new_element, None, None, node.get_depth()+1))

                pai_rarrow = self.get_right_arrow(element)
                
                self.tudo += self.get_vnode(new_element)
                self.tudo += pai_rarrow
                
                if self.tudo.width < self.tudo.height:
                    self.play(
                        FadeIn(self.get_vnode(new_element)),
                        GrowArrow(pai_rarrow),
                        self.camera.frame.animate.set(height=self.tudo.height * 1.5).move_to(self.tudo.get_center())
                            )
                else:
                    self.play(
                        FadeIn(self.get_vnode(new_element)),
                        GrowArrow(pai_rarrow),
                        self.camera.frame.animate.set(width=self.tudo.width * 1.5).move_to(self.tudo.get_center())
                            )
                return True
            else:
                r_arrow = self.get_right_arrow(element)
                r_son = self.get_vnode(node.get_right().get_item())

                self.play(
                        r_arrow.animate.set_color(color=RED),
                        r_son.animate.set_color(color=RED, family=True), run_time=0.8
                        )
                return self.rinsert(node.get_right(), item)

        return False

    def rinorder(self, node):
        if node.get_left() != None:
            self.rinorder(node.get_left())

        item = self.get_vitem(node.get_item()).original_text
        if item not in self.visited:
            self.visited.append(item)
            circle = self.get_circle(node.get_item())
            self.circles.append(circle)

            self.play(
                    circle.animate.set_fill(color=GREEN, opacity=0.4, family=True))

        if node.get_right() != None:
            self.rinorder(node.get_right())

    def in_order(self):
        if self.root == None:
            self.print("Árvore vazia.")
            return

        self.visited = []
        self.circles = []

        self.rinorder(self.root)

        circles = VGroup()
        for c in self.circles:
            circles += c

        self.play(
                circles.animate.set_fill(opacity=0), run_time=0.4
                )

        print(self.visited)


    def construct(self):
        self.O_WIDTH = self.camera.frame.width
        self.root = None    

        self.MIN_E_WIDTH = 2
        self.E_HEIGHT = 4
        self.max_width = 4
        self.max_depth = 0
        self.MIN_A_SIZE = 2

        self.tudo = VGroup()

       #self.insert(5)
       #self.insert(2)
       #self.insert(3)
       #self.insert(8)
       #self.insert(6)
       #self.insert(7)
       #self.insert(10)
       #self.in_order()

       #self.search(4)

       #self.wait(2)
