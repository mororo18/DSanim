from manim import *



class ListSeq(MovingCameraScene):
    def bounds(self, i):
        if i >= self.size or i < 0:
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
        if self.bounds(i) == False:
            self.print("Remoção inválida na posição {}.".format(i))
            return

        self.play(FadeOut(self.get_label(i)))
        self.set_label(i, Text("")) 

        if i < self.size:
            self.shift(i+1, -1)

        self.size -= 1

    def shift(self, pos, offset):
        I = list(range(pos, self.size))
        print(I)

        coef = 0.9

        if offset > 0:
            I.reverse()

            for i in I:
                #self.play(FadeOut(self.array[i][1]))
                self.play(self.get_label(i).animate.move_to(self.get_square(i+offset).get_center()), run_time=coef)
                coef *= coef

                self.set_label(i+offset, self.get_label(i))
        elif offset < 0:
            for i in I:
                self.set_label(i+offset, Text(""))
                self.set_label(i+offset, self.get_label(i))
                self.add(self.get_label(i))

                self.play(self.get_label(i).animate.move_to(self.get_square(i+offset).get_center()), run_time=coef)
                coef *= coef

    def insert(self, i, e):
        if self.bounds(i) == False and i > self.size:
            self.print("Inserção inválida na posição {}.".format(i))
            return

        if self.size == self.get_max():
            self.print("Capacidade máxima atingida.")
            return


        label = Text("{}".format(e)).move_to(self.get_square(i).get_center())
        if i < self.size:
            self.shift(i, 1)
            #print("shift pae")
        #self.array[i] = self.build_VGroup(square=self.get_square(i), label=label, index=self.get_index(i))
        self.set_label(i, label)

        self.size += 1

        self.play(FadeIn(label))

       #if i == 0:
       #    box = Square()
       #elif self.bounds(i) or i == len(self.itens):
       #    box = Square().next_to(self.itens[i-1])
       #else:
       #    self.print("Inserção inválida na posição {}.".format(i))
       #    return

       #text = Text("{}".format(e)).move_to(box.get_center())
       #item = VGroup(box, text)
       #self.itens.insert(i, item)

       #cpy = self.itens.copy()
       #cpy[i+1:].next_to(item)

       #self.play(self.itens[i+1:].animate.next_to(item),
       #    self.camera.frame.animate.set(width=cpy.width * 2.1).move_to(cpy.get_center() ))
       #self.play(FadeIn(item))

    def build_VGroup(self, square, index, label):
        return VGroup(square, index, label)

    def search(self, x):
        for i, item in enumerate(self.array):
            if x == int(self.get_label(i).original_text):
                if i == 0:
                    self.play(item.animate.set_color(color=GREEN, family=True))
                else:
                    self.play(item.animate.set_color(color=GREEN, family=True), self.array[i-1].animate.set_color(color=WHITE, family=True))

                self.print("Item {} encontrado na posição {}.".format(x, i))
                self.play(item.animate.set_color(color=WHITE, family=True))
                break
            else:
                if i == 0:
                    self.play(item.animate.set_color(color=RED, family=True))
                else:
                    self.play(item.animate.set_color(color=RED, family=True), self.array[i-1].animate.set_color(color=WHITE, family=True))

    def set_square(self, i, square):
        self.array[i][0] = square

    def set_index(self, i, index):
        self.array[i][1] = index

    def set_label(self, i, label):
        self.array[i][2] = label

    def get_square(self, i):
        return self.array[i][0]
    def get_index(self, i):
        return self.array[i][1]
    def get_label(self, i):
        return self.array[i][2]

    def get_max(self):
        return len(self.array)

    def add_elements(self, n):
        new_g = VGroup()
        for i in range(self.get_max(), self.get_max()+ n):
            if i > 0:
                s = Square().next_to(self.get_square(-1))
            else:
                s = Square()
            index = Text("{}".format(i)).next_to(s, DOWN).scale(0.7)
            item = Text("")
            
            new = VGroup(s, index, item)
            self.array.add(new)
            new_g.add(new)

        self.play(
            FadeIn(new_g),
            self.camera.frame.animate.set(width=self.array.width * 1.5).move_to(self.array.get_center())
            )

    def rm_elements(self, n):
        if n > self.get_max():
            self.print("Operação Inválida!")
            return

        new_g = self.array[-n:]
        self.array = self.array[:-n]

        if self.get_max() < self.size:
            self.size = self.get_max()

        
        self.play(
            FadeOut(new_g),
            self.camera.frame.animate.set(width=self.array.width * 1.5).move_to(self.array.get_center())
            )

       #for i in range(self.get_max(), self.get_max()+ n):
       #    if i > 0:
       #        s = Square().next_to(self.get_square(-1))
       #    else:
       #        s = Square()
       #    index = Text("{}".format(i)).next_to(s, DOWN).scale(0.7)
       #    item = Text("")
       #    
       #    new = VGroup(s, index, item)
       #    self.array.add(new)
       #    new_g.add(new)
    def resize(self, size):
        diff = size - self.get_max()
        if diff > 0:
            self.add_elements(diff)
        elif diff < 0:
            self.rm_elements(-diff)

    def construct(self):

        self.itens = VGroup()
        self.O_WIDTH = self.camera.frame_width

        self.size = 0

        self.array = VGroup()

        #self.add_elements(15)




       #self.insert(0, 3)
       #self.insert(1, 8)
       #self.insert(1, 11)
       #self.insert(1, 5)
       #self.erase(0)
       #self.erase(0)
       #self.insert(1, -2)
       #self.insert(1, 11)
       #self.insert(1, 5)
       #self.search(-2)
       ##self.erase(0)
       #self.insert(4, 7)
       #self.insert(5, 14)
       #self.insert(6, 93)
       #self.insert(1, 11)
       #self.erase(1)
       #self.erase(14)
       #self.insert(0, 0)
       #self.resize(18)
       #self.wait(2)
       #self.resize(6)

       # self.wait(2)
