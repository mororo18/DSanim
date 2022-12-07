from manim import *



class Stack(MovingCameraScene):
    def bounds(self, i):
        if i > self.get_size() or i < 0:
            return False
        else:
            return True

    def print(self, text):
        prompt=Text(text).move_to(self.camera.frame_center).scale(self.camera.frame_width / self.O_WIDTH).set_color(BLACK)
        box = Rectangle(width=prompt.width*1.1 , height = prompt.height + prompt.width*0.1).move_to(self.camera.frame_center).set_color(BLACK)
        box.set_fill(WHITE, 0.8)

        label = VGroup(box, prompt)

        self.play(FadeIn(label), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(label), run_time=0.5)

    def erase(self, i):
        if self.bounds(i) == False or self.get_size() == i:
            self.print("Remoção inválida na posição {}.".format(i))
            return

        if i == self.get_size()-1:
            if self.get_size() == 1:
                arrow = self.get_arrow_head()
            else:
                arrow = self.get_arrow(-2)

            last = self.array[-1]
            last -= self.get_arrow(-1)

            self.array -= last


            tudo = self.get_tudo()
            self.play(
                    FadeOut(last),
                    FadeOut(arrow),
                    self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
                )
        
        elif i > 0:
            aux = self.build_element_single("aux", self.get_rect(i).get_center() + UP*4)

            tudo = self.get_tudo()
            tudo += aux
            self.play(
                    FadeIn(aux[:-1]),
                    self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
                    )
            arrow = Arrow(start = aux[0].get_center(), end = self.get_center_left(i+1) + UL*1.1)
            self.play(GrowArrow(arrow))

            erased = self.array[i]
            pre_arrow = self.get_arrow(i-1)

            self.array -= erased

            indices = VGroup()
            indices_new = VGroup()
            for el in self.array[i:]:
                print(el[1])
                indices.add(el[1])
                new_index = "{}".format(int(el[1].original_text)-1)
                indices_new.add(Text(new_index).scale(0.6).move_to(el[1]))
                el[1].original_text = new_index

            self.play(
                    FadeOut(erased),
                    FadeOut(pre_arrow),
                    Transform(indices, indices_new)
                    )

            resto_cpy = self.array[i:].copy().next_to(self.array[:i])
            new_tudo = VGroup(self.head, self.array[:i], resto_cpy)
            aux -= aux[2]

            # remove a seta do final
            last = self.array[-1]
            last -= self.get_arrow(-1)

            self.play(
                    FadeOut(aux),
                    Transform(arrow, self.get_arrow(i-1)),
                    self.array[i:].animate.next_to(self.array[:i]),
                    self.camera.frame.animate.set(width=new_tudo.width * 1.5).move_to(new_tudo.get_center())
                    )

            # add uma seta (invisivel) no final
            arrow = Arrow(start=self.get_center_right(-1), end=self.get_center_right(-1) + self.A_SIZE*RIGHT)
            self.array[-1].add(arrow) 
            self.remove(arrow) 

        else: # i == 0
            aux = self.build_element_single("aux", self.get_rect(i).get_center() + UP*4)
            #c_arrow  = CurvedArrow(start_point= self.get_center_right(i-1), end_point= self.get_center_left(i+1)+DL*1.1, stroke_width=6)
            #print(c_arrow)
            tudo = self.get_tudo()
            tudo += aux
            self.play(
                    FadeIn(aux[:-1]),
                    self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
                    )
            arrow = Arrow(start = aux[0].get_center(), end = self.get_center_left(i+1) + UL*1.1)
            self.play(GrowArrow(arrow))

            erased = self.array[i]
            pre_arrow = self.get_arrow_head()

            self.array -= erased

            indices = VGroup()
            indices_new = VGroup()
            for el in self.array[i:]:
                print(el[1])
                indices.add(el[1])
                new_index = "{}".format(int(el[1].original_text)-1)
                indices_new.add(Text(new_index).scale(0.6).move_to(el[1]))
                el[1].original_text = new_index

            self.play(
                    FadeOut(erased),
                    FadeOut(pre_arrow),
                    Transform(indices, indices_new)
                    )

            resto_cpy = self.array[i:].copy().next_to(self.array[:i])
            new_tudo = VGroup(self.head, resto_cpy)
            aux -= aux[2]

            # remove a seta do final
            last = self.array[-1]
            last -= self.get_arrow(-1)

            self.play(
                    FadeOut(aux),
                    Transform(arrow, self.get_arrow_head()),
                    self.array[i:].animate.next_to(self.head),
                    self.camera.frame.animate.set(width=new_tudo.width * 1.5).move_to(new_tudo.get_center())
                    )

            # add uma seta (invisivel) no final
            arrow = Arrow(start=self.get_center_right(-1), end=self.get_center_right(-1) + self.A_SIZE*RIGHT)
            self.array[-1].add(arrow) 
            self.remove(arrow) 


   #def insert(self, i, e):
   #    if self.bounds(i) == False and i > self.size:
   #        self.print("Inserção inválida na posição {}.".format(i))
   #        return

   #    if i == self.get_size():
   #        self.push_back(e)

   #    elif i > 0:
   #        pos = [-1, 2, 0]
   #        element = self.build_element(i, e, ORIGIN).next_to(self.get_center_left(i) + pos, direction = UP)

   #        before_g = self.array[:i]
   #        after_g = self.array[i:]

   #        self.array = VGroup()
   #        for g in before_g:
   #            self.array.add(g)
   #        self.array.add(element)
   #        for g in after_g:
   #            self.array.add(g)

   #       #in_arrow = Arrow(start=self.get_center_right(i-1), 
   #       #        end = self.get_center_left(i))
   #       #d = self.get_center_left(i) - self.get_center_right(i-1)
   #       #length = in_arrow.get_length()
   #       #norm_d = d / length
   #       #d -= norm_d

   #       #in_arrow.put_start_and_end_on(start=self.get_center_right(i-1), end = self.get_center_right(i-1)+d)

   #        out_arrow = Arrow(start=self.get_center_right(i), 
   #                end = self.get_center_left(i+1))
   #        d = self.get_center_left(i+1) - self.get_center_right(i)
   #        length = out_arrow.get_length()
   #        norm_d = d / length
   #        d -= norm_d

   #        out_arrow.put_start_and_end_on(start=self.get_center_right(i), end = self.get_center_right(i)+d)

   #        indices = VGroup()
   #        indices_new = VGroup()
   #        for el in after_g:
   #            print(el[1])
   #            indices.add(el[1])
   #            new_index = "{}".format(int(el[1].original_text)+1)
   #            indices_new.add(Text(new_index).scale(0.6).move_to(el[1]))
   #            el[1].original_text = new_index

   #        aux = self.build_element_single("aux", element[0].get_center() + LEFT*5)

   #        tudo = self.get_tudo()
   #        tudo += aux
   #        self.play(
   #            FadeIn(element[:-1]),
   #            FadeIn(aux),
   #            self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
   #            )
   #        self.play(
   #                #GrowArrow(in_arrow),
   #                GrowArrow(out_arrow),Transform(indices, indices_new))

   #        self.play(FadeOut(self.get_arrow(i-1)))
   #        e_cpy = element.copy().next_to(self.array[i-1])
   #        out_cpy = e_cpy[3]


   #        # remove a seta do final
   #        last = self.array[-1]
   #        last -= self.get_arrow(-1)

   #        # cria novo 'tudo'
   #        array_cpy = self.array.copy() - element
   #        new_tudo = VGroup(self.head, array_cpy)
   #        ne = self.build_element(0, 0, ORIGIN).next_to(array_cpy)
   #        new_tudo.add(ne)
   #        
   #        aux_arrow = aux[2]
   #        aux -= aux[2]
   #        self.play(
   #                FadeOut(aux),
   #                Transform(aux_arrow, self.get_arrow(i-1)),
   #                Transform(out_arrow, out_cpy),
   #                element[:-1].animate.next_to(self.array[i-1]),
   #                after_g.animate.next_to(e_cpy),
   #                self.camera.frame.animate.set(width=new_tudo.width * 1.5).move_to(new_tudo.get_center())
   #            )


   #        self.set_arrow(i-1, aux_arrow)
   #        self.set_arrow(i, out_arrow)

   #        # add uma seta (invisivel) no final
   #        arrow = Arrow(start=self.get_center_right(-1), end=self.get_center_right(-1) + self.A_SIZE*RIGHT)
   #        self.array[-1].add(arrow) 
   #        self.remove(arrow) 
   #    else: # i==0
   #        print("pqp")
   #        pos = [-1, 2, 0]
   #        head_rect = self.get_rect_head()
   #        element = self.build_element(i, e, ORIGIN).next_to(self.get_center_left(i) + pos, direction = UP)

   #        after_g = self.array[i:]

   #        self.array = VGroup()
   #        self.array.add(element)
   #        for g in after_g:
   #            self.array.add(g)

   #       #in_arrow = Arrow(start=head_rect.get_center(), 
   #       #        end = self.get_center_left(i))
   #       #d = self.get_center_left(i) - head_rect.get_center()
   #       #length = in_arrow.get_length()
   #       #norm_d = d / length
   #       #d -= norm_d

   #       #in_arrow.put_start_and_end_on(start=head_rect.get_center(), end = head_rect.get_center()+d)

   #        out_arrow = Arrow(start=self.get_center_right(i), 
   #                end = self.get_center_left(i+1))
   #        d = self.get_center_left(i+1) - self.get_center_right(i)
   #        length = out_arrow.get_length()
   #        norm_d = d / length
   #        d -= norm_d

   #        out_arrow.put_start_and_end_on(start=self.get_center_right(i), end = self.get_center_right(i)+d)

   #        indices = VGroup()
   #        indices_new = VGroup()
   #        for el in after_g:
   #            print(el[1])
   #            indices.add(el[1])
   #            new_index = "{}".format(int(el[1].original_text)+1)
   #            indices_new.add(Text(new_index).scale(0.6).move_to(el[1]))
   #            el[1].original_text = new_index

   #        aux = self.build_element_single("aux", element[0].get_center() + LEFT*5)

   #        tudo = self.get_tudo()
   #        tudo += aux
   #        self.play(
   #            FadeIn(aux),
   #            FadeIn(element[:-1]),
   #            self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
   #            )
   #        self.play(
   #                #GrowArrow(in_arrow),
   #                GrowArrow(out_arrow),Transform(indices, indices_new)
   #            )

   #        self.play(FadeOut(self.get_arrow_head()))
   #        e_cpy = element.copy().next_to(self.head)
   #        out_cpy = e_cpy[3]


   #        # remove a seta do final
   #        last = self.array[-1]
   #        last -= self.get_arrow(-1)


   #        # cria novo 'tudo'
   #        array_cpy = self.array.copy() - element
   #        new_tudo = VGroup(self.head, array_cpy)
   #        ne = self.build_element(0, 0, ORIGIN).next_to(array_cpy)
   #        new_tudo.add(ne)

   #        aux_arrow = aux[2]
   #        aux -= aux[2]
   #        self.play(
   #                FadeOut(aux),
   #                Transform(aux_arrow, self.get_arrow_head()),
   #                Transform(out_arrow, out_cpy),
   #                element[:-1].animate.next_to(self.head),
   #                after_g.animate.next_to(e_cpy),
   #                self.camera.frame.animate.set(width=new_tudo.width * 1.5).move_to(new_tudo.get_center())
   #            )


   #        self.set_arrow_head(aux_arrow)
   #        self.set_arrow(i, out_arrow)

   #        # add uma seta (invisivel) no final
   #        arrow = Arrow(start=self.get_center_right(-1), end=self.get_center_right(-1) + self.A_SIZE*RIGHT)
   #        self.array[-1].add(arrow) 
   #        self.remove(arrow) 


    def build_rect(self, pos):
        return Rectangle(width = 4, height=2, grid_xstep=2).move_to(pos)
    def build_element(self, index, label, pos):
        rect = self.build_rect(pos)
        #i = Text(".").scale(0.6).next_to(rect, direction=DOWN)
        l = Text("{}".format(label)).move_to(rect.get_center() + [1, 0, 0])
        c = rect.get_center() - [1, 0, 0]
        return VGroup(rect, l, Arrow(start=c, end=c + self.A_SIZE*LEFT))
    def build_element_single(self, label, pos):
        s = Square().move_to(pos)
        t_label = Text(label).scale(0.6).next_to(s, direction=UP)
        return VGroup(s, t_label, Arrow(start=s.get_center(), end=s.get_center() + self.A_SIZE*DOWN))
    def build_head(self, pos):
        s = Square().move_to(pos)
        t_label = Text("Base").scale(0.6).next_to(s, direction=UP)
        return VGroup(s, t_label, Arrow(start=s.get_center(), end=s.get_center() + self.A_SIZE*DOWN))
    def build_tail(self, pos):
        s = Square().move_to(pos)
        t_label = Text("Top").scale(0.6).next_to(s, direction=DOWN)
        return VGroup(s, t_label, Arrow(start=s.get_center(), end=s.get_center() + self.A_SIZE*UP))

    def search(self, x):
        for i, item in enumerate(self.array):
            if x == int(self.get_label(i).original_text):
                if i == 0:
                    self.play(item[:-1].animate.set_color(color=GREEN, family=True))
                else:
                    self.play(item[:-1].animate.set_color(color=GREEN, family=True), self.array[i-1][:-1].animate.set_color(color=WHITE, family=True))

                self.print("Item {} encontrado na posição {}.".format(x, i))
                self.play(item[:-1].animate.set_color(color=WHITE, family=True))
                return
            else:
                if i == 0:
                    self.play(item[:-1].animate.set_color(color=RED, family=True))
                else:
                    self.play(item[:-1].animate.set_color(color=RED, family=True), self.array[i-1][:-1].animate.set_color(color=WHITE, family=True))

        self.play(self.array[-1][:-1].animate.set_color(color=WHITE, family=True))
        self.print("Item {} não encontrado.".format(x))

    def set_square(self, i, square):
        self.array[i][0] = square
    def set_index(self, i, index):
        self.array[i][1] = index
    def set_label(self, i, label):
        self.array[i][1] = label
    def set_arrow(self, i, arrow):
        self.array[i][2] = arrow

    def get_rect_e(self, e):
        return e[0]
    def get_index_e(self, e):
        return e[1]
    def get_label_e(self, e):
        return e[1]
    def get_arrow_e(self, e):
        return e[2]


    def get_rect(self, i):
        return self.array[i][0]
    def get_index(self, i):
        return self.array[i][1]
    def get_label(self, i):
        return self.array[i][1]
    def get_arrow(self, i):
        return self.array[i][2]

    def get_rect_head(self):
        return self.head[0]
    def get_arrow_head(self):
        return self.head[2]

    def get_rect_tail(self):
        return self.tail[0]
    def get_arrow_tail(self):
        return self.tail[2]

    def set_arrow_head(self, a):
        self.head[2] = a

    def set_arrow_tail(self, a):
        self.tail[2] = a

    def get_center_left_e(self, e):
        return self.get_rect_e(e).get_center() - [1, 0, 0]
    def get_center_right_e(self, e):
        return self.get_rect_e(e).get_center() + [1, 0, 0]

    def get_center_left(self, i):
        return self.get_rect(i).get_center() - [1, 0, 0]
    def get_center_right(self, i):
        return self.get_rect(i).get_center() + [1, 0, 0]

    def get_size(self):
        return len(self.array)

    def get_tudo(self):
        return VGroup(self.head, self.tail, self.array)

    def get_dim_maior(self, tudo):
        maior = tudo.width
        if maior < tudo.height:
            maior = tudo.height
        return maior

    def top(self):
        if self.get_size() == 0:
            self.print("Pilha vazia!")
            return
        self.print("O primeiro item da pilha: {}".format(self.get_label(0).original_text))

    def pop(self):

        if self.get_size() == 0:
            self.print("Pilha vazia!")
            return

        if self.get_size() == 1:
            self.play(
                FadeOut(self.get_arrow_tail()),
                FadeOut(self.get_arrow_head())
                    )
            front = self.array[0]
            self.array -= front

            tudo = self.get_tudo()
            self.play(
                    FadeOut(front[:-1])
                    )
        else:
            new_last = self.array[-2]
            #self.play()

            last = self.array[-1]
            self.array -= last

            tudo = self.get_tudo()
            self.play(
                FadeOut(last),
                self.tail.animate.next_to(new_last[:-1], direction=DOWN),
                self.camera.frame.animate.set(width=tudo.width * 1.5, height=tudo.height*1.5).move_to(tudo.get_center())
                    )

    def push(self, e):
        if self.get_size() == 0:
            element = self.build_element(self.get_size(), e, ORIGIN).next_to(self.head, direction=DOWN)
            

            self.array.add(element)
            tudo = self.get_tudo()

            head_arrow = self.get_arrow_head()
            tail_arrow = self.get_arrow_tail()

            head_cpy = self.head.copy()
            tail_cpy = self.tail.copy()

            head_cpy.next_to(element[:-1], direction=UP),
            tail_cpy.next_to(element[:-1], direction=DOWN),

            tudo += head_cpy
            tudo += tail_cpy
            
            self.play(
                FadeIn(element[:-1]),
                self.head[:-1].animate.move_to(head_cpy[:-1].get_center()),
                self.tail[:-1].animate.move_to(tail_cpy[:-1].get_center()),
                self.camera.frame.animate.set(width=tudo.width * 1.5, height=tudo.height*1.5).move_to(tudo.get_center())
            )

            d = self.A_SIZE * DOWN *0.9
            head_arrow.put_start_and_end_on(start=self.get_rect_head().get_center(), end = self.get_rect_head().get_center()+d)

            d = self.A_SIZE * UP * 0.9
            tail_arrow.put_start_and_end_on(start=self.get_rect_tail().get_center(), end = self.get_rect_tail().get_center()+d)

            self.play(GrowArrow(self.get_arrow_head()),
                GrowArrow(self.get_arrow_tail()))
        else:
            element = self.build_element(self.get_size(), e, ORIGIN).next_to(self.array[-1])

            self.array.add(element)
            tudo = self.get_tudo()
            self.play(
                FadeIn(element[:-1]),
                GrowArrow(self.get_arrow(-1)),
                self.tail.animate.next_to(element[:-1], direction=DOWN),
                self.camera.frame.animate.set(width=tudo.width * 1.5, height=tudo.height*1.5).move_to(tudo.get_center())
            )
            #self.play()



    def construct(self):

        self.itens = VGroup()
        self.O_WIDTH = self.camera.frame_width

        self.A_SIZE = 3


        self.array = VGroup()

        self.head = self.build_head(ORIGIN)
        self.tail = self.build_tail(ORIGIN).next_to(self.head, direction=DOWN)
        self.camera.frame.set(width=(self.get_tudo().width * 1.5), height= (self.get_tudo().height * 1.5)).move_to(self.get_tudo().get_center())

        self.play(FadeIn(self.head[:-1]),
            FadeIn(self.tail[:-1]))


       #self.push_back(2)
       #self.push_back(2)
       #self.push_back(58)
       #self.pop_back()
       #self.pop_back()
       #self.pop_back()
       #self.push_back(58)
       #self.push_back(58)
       #self.pop_back()
        #self.push_back(2)
        #self.push_back(-12)

       #element = self.build_element(0, 3, ORIGIN).next_to(self.head)

       #tudo = VGroup(self.head, element)
       #self.play(
       #    FadeIn(element[:-1]),
       #    self.camera.frame.animate.set(width=tudo.width * 1.5).move_to(tudo.get_center())
       #)
       #self.play(GrowArrow(self.head[2]))

       #rect = Rectangle(height=1, width=2, grid_xstep=1)
       #self.play(FadeIn(rect))

       #item = Text("{}".format(2)).move_to(rect.get_center() + [-0.5, 0, 0])
       #self.play(FadeIn(item))

       #index = Text("{}".format(0)).next_to(rect, direction=DOWN).scale(0.6)
       #self.play(FadeIn(index))

       #p = rect.get_center() + [0.5, 0, 0]
       #seta = Arrow(start=p, end=p+[2, 0,0] , color=WHITE)
       ##seta = Arrow(radius=0.05, color=WHITE, fill_opacity=1).move_to(rect.get_center() + [0.5, 0, 0])
       #self.play(FadeIn(seta))


