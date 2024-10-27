inputs = ['1.in', '2.in', '3.in', '4.in', '5.in', '6.in', '11.in', '12.in']
outputs = ['1.out', '2.out', '3.out', '4.out', '5.out', '6.out', '11.out', '12.out']

for i_file in range(len(inputs)):
    with open(f'tests/{inputs[i_file]}') as file:
        lines = file.read().split('\n')[:-1]

    n_table = int(lines[0])
    lines = lines[1:]
    count_rows = [int(elem) for elem in lines[0].split()]
    lines = lines[1:]

    cards = [dict() for _ in range(n_table)]
    n = int(lines[0])
    lines = lines[1:]
    for i in range(n):
        a, b, c = lines[i].split()
        cards[int(a) - 1][f'{int(a)}.{b}'] = int(c)
    lines = lines[n:]

    n = int(lines[0])
    lines = lines[1:]
    scan_preds = [[] for _ in range(n_table)]
    for i in range(n):
        a, b = lines[i].split()
        scan_preds[int(a) - 1].append(f'{int(a)}.{b}')
    lines = lines[n:]

    n = int(lines[0])
    lines = lines[1:]
    join_preds = []
    for i in range(n):
        a, b, c, d = lines[i].split()
        join_preds.append([int(a), int(b), c, d])


    print('---------------------------------------------------------------------------')
    print(f"Тест {inputs[i_file]}")
    print("Количество таблиц:", n_table)
    print("Количество строк в таблицах:", count_rows)
    print("Атрибуты с координальностями:", cards)
    print("Предикаты на скан:", scan_preds)
    print("Джоин предикатов:", join_preds)

    with open(f'tests/task1/{outputs[i_file]}') as file:
        print(file.read().split('\n')[0])


# n_table = int(input())
# count_rows = [int(elem) for elem in input().split()]
#
# cards = [dict() for _ in range(n_table)]
# for i in range(int(input())):
#     a, b, c = input().split()
#     cards[int(a) - 1][f'{int(a)}.{b}'] = int(c)
#
# scan_preds = [[] for _ in range(n_table)]
# for i in range(int(input())):
#     a, b = input().split()
#     scan_preds[int(a) - 1].append(f'{int(a)}.{b}')
#
# join_preds = []
# for i in range(int(input())):
#     a, b, c, d = input().split()
#     join_preds.append([int(a), int(b), c, d])
#
# print("Количество таблиц:", n_table)
# print("Количество строк в таблицах:", count_rows)
# print("Атрибуты с координальностями:", cards)
# print("Предикаты на скан:", scan_preds)
# print("Джоин предикатов:", join_preds)

    class Tree:
        def __init__(self, cost: int = 0, rows: int = 0, numbers: list = None, attributes_with_cord=None,
                     leftSubtree=None,
                     rightSubtree=None,
                     leftPredicats=None, rightPredicats=None, predicats=None):

            if attributes_with_cord is None:
                self.attributes_with_cord = {}
            if rightPredicats is None:
                rightPredicats = []
            if leftPredicats is None:
                leftPredicats = []
            if predicats is None:
                predicats = []

            self.numbers = numbers
            self.cost = cost
            self.rows = rows
            self.attributes_with_cord = attributes_with_cord
            self.leftSubtree = leftSubtree
            self.rightSubtree = rightSubtree
            self.leftPredicats = leftPredicats
            self.rightPredicats = rightPredicats
            self.predicats = predicats
            self.need_calculate = True

        def cost_nest_loop_inner(self):
            return (self.leftSubtree.cost + self.rightSubtree.cost +
                    self.rightSubtree.rows * 1.1 +
                    (self.leftSubtree.rows - 1) * self.rightSubtree.rows +
                    self.rows * 0.1)

        def cost_hash(self):
            return (self.leftSubtree.cost + self.rightSubtree.cost +
                    self.rightSubtree.rows * 1.5 +
                    self.leftSubtree.rows * 3.5 +
                    self.rows * 0.1)

        def cost_join(self):
            return min(self.cost_nest_loop_inner(), self.cost_hash())

        def cost_nest_loop_cross(self):
            return (self.leftSubtree.cost + self.rightSubtree.cost +
                    self.rightSubtree.rows * 0.2 +
                    (self.leftSubtree.rows - 1) * self.rightSubtree.rows * 0.1)

        def scan_with_pred(self, pred_attr):
            self.rows /= self.attributes_with_cord[pred_attr]

        def scan_with_multi_pred(self):
            if self.leftSubtree is None and self.rightSubtree is None:
                if len(self.predicats) == 0:
                    self.cost = self.rows
                else:
                    self.cost = 2 * self.rows

            for pred_attr in self.predicats:
                self.scan_with_pred(pred_attr)

        def rows_join(self):
            self.rows = self.leftSubtree.rows * self.rightSubtree.rows
            for pred_left, pred_right in zip(self.leftPredicats, self.rightPredicats):
                # print('keys ', pred_left, pred_right)
                # print('maps ', self.leftSubtree.attributes_with_cord, self.rightSubtree.attributes_with_cord)
                self.rows /= max(self.leftSubtree.attributes_with_cord[pred_left],
                                 self.rightSubtree.attributes_with_cord[pred_right])

        def calculate(self):
            if self.need_calculate:
                # Выполняем предикаты в данной вершине
                self.scan_with_multi_pred()

                if not self.leftSubtree is None and not self.rightSubtree is None:
                    self.leftSubtree.calculate()
                    self.rightSubtree.calculate()

                    # атрибуты в итоговом дереве - атрибуты поддеревьев
                    self.attributes_with_cord = self.leftSubtree.attributes_with_cord.copy()
                    self.attributes_with_cord.update(self.rightSubtree.attributes_with_cord)

                    # выделяем множество вершин
                    self.numbers = self.leftSubtree.numbers + self.rightSubtree.numbers

                    # Вычисляем количество строк
                    self.rows_join()
                    # Вычисляем стоимость
                    if self.leftPredicats and self.rightPredicats:
                        self.cost = self.cost_join()
                    else:
                        self.cost = self.cost_nest_loop_cross()
                self.need_calculate = False

        def output(self):
            if self.leftSubtree is None and self.rightSubtree is None:
                result = str(self.numbers[0])
                for predicat in self.predicats:
                    result += predicat.split('.')[1]
                return result
            else:
                result = '(' + self.leftSubtree.output() + ' ' + self.rightSubtree.output()
                for pred_left, pred_right in zip(self.leftPredicats, self.rightPredicats):
                    result += ' {' + pred_left + ' ' + pred_right + '}'
                result += ')'
                return result

        def __str__(self):
            return f'''Количество строк {self.rows}
            Стоимость {self.cost}
            Атрибуты с координальностями {self.attributes_with_cord}
            Предикаты {self.predicats}
            Какие вершины тут {self.numbers}
            Левое поддерево :\n{self.leftSubtree}
            Правое поддерево :\n{self.rightSubtree}'''


    def calc(node_i, node_j):
        left = []
        right = []
        for join in join_preds:
            if join[0] in node_i.numbers and join[1] in node_j.numbers:
                left.append(str(join[0]) + '.' + join[2])
                right.append(str(join[1]) + '.' + join[3])
            elif join[1] in node_i.numbers and join[0] in node_j.numbers:
                left.append(str(join[1]) + '.' + join[3])
                right.append(str(join[0]) + '.' + join[2])
        join = Tree(leftSubtree=node_i, rightSubtree=node_j, leftPredicats=left, rightPredicats=right)
        join.calculate()
        return join


    nodes = []

    for i in range(len(count_rows)):
        nodes.append(Tree(rows=count_rows[i], attributes_with_cord=cards[i], predicats=scan_preds[i], numbers=[i + 1]))

    while len(nodes) > 1:
        result_nodes = []
        # if len(nodes) >= 3:
        #     best_indexes = [0, 1, 2, 1]
        #     precalc = calc(nodes[0], nodes[1])
        #     precalc_1 = calc(precalc, nodes[2])
        #     best_rows = precalc_1.rows
        #     best_cost = precalc_1.cost
        #
        #     for i in range(len(nodes)):
        #         for j in range(len(nodes)):
        #             for k in range(len(nodes)):
        #                 if i == j or j == k or i == k:
        #                     continue
        #                 join = calc(nodes[i], nodes[j])
        #                 join_1 = calc(join, nodes[k])
        #                 if join_1.rows < best_rows or (join_1.rows == best_rows and join_1.cost < best_cost):
        #                     best_rows = join_1.rows
        #                     best_cost = join_1.cost
        #                     best_indexes = [i, j, k, 1]
        #                 join = calc(nodes[j], nodes[k])
        #                 join_1 = calc(nodes[i], join)
        #                 if join_1.rows < best_rows or (join_1.rows == best_rows and join_1.cost < best_cost):
        #                     best_rows = join_1.rows
        #                     best_cost = join_1.cost
        #                     best_indexes = [i, j, k, 2]
        #     if best_indexes[3] == 1:
        #         result_nodes.append(calc(calc(nodes[best_indexes[0]], nodes[best_indexes[1]]), nodes[best_indexes[2]]))
        #     elif best_indexes[3] == 2:
        #         result_nodes.append(calc(nodes[best_indexes[0]], calc(nodes[best_indexes[1]], nodes[best_indexes[2]])))
        #     for i, node in enumerate(nodes):
        #         if i != best_indexes[0] and i != best_indexes[1] and i != best_indexes[2]:
        #             result_nodes.append(node)
        if len(nodes) >= 2:
            best_indexes = [0, 1]
            precalc = calc(nodes[0], nodes[1])
            best_rows = precalc.rows
            best_cost = precalc.cost

            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    if i == j:
                        continue
                    join = calc(nodes[i], nodes[j])
                    if join.rows < best_rows or (join.rows == best_rows and join.cost < best_cost):
                        best_rows = join.rows
                        best_cost = join.cost
                        best_indexes = [i, j]
            result_nodes.append(calc(nodes[best_indexes[0]], nodes[best_indexes[1]]))
            for i, node in enumerate(nodes):
                if i != best_indexes[0] and i != best_indexes[1]:
                    result_nodes.append(node)
        nodes = result_nodes.copy()

    ans = nodes[0]
    print(ans.output(), ans.cost)

