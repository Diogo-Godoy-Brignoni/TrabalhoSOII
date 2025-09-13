from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import math
import sys

# Visualização

def map(cells: List[Optional[str]], width=60):
    n = len(cells)
    group_size = max(1, n // width)
    chars = []
    for i in range(0, n, group_size):
        group = cells[i:i+group_size]
        if all(x is None for x in group):
            chars.append('.')
        elif all(x is not None for x in group):
            chars.append('#')
        else:
            chars.append('~')
    print('[' + ''.join(chars) + ']')
    print('. = livre | # = ocupado | ~ = fragmentado')

# Dataclasses

@dataclass
class Process:
    pid: int
    size: int
    base: int
    limit: int

@dataclass
class Pag:
    page_number: int
    frame_number: Optional[int]

# Alocador Contíguo Dinâmico

class Contiguo:
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.free_list: List[Tuple[int, int]] = [(0, total_size)]
        self.allocated: Dict[int, Process] = {}
        self._last_circular_index = 0

    def update_free_list(self, new_free_list):
        fl = sorted(new_free_list, key=lambda x: x[0])
        list = []
        for base, size in fl:
            if size <= 0:
                continue
            if not list:
                list.append((base, size))
            else:
                last_base, last_size = list[-1]
                if last_base + last_size >= base:
                    new_size = max(last_base + last_size, base + size) - last_base
                    list[-1] = (last_base, new_size)
                else:
                    list.append((base, size))
        self.free_list = list

    def create_process(self, pid: int, size: int, model: str) -> bool:
        hole = None
        if model == 'first':
            for i, (base, sz) in enumerate(self.free_list):
                if sz >= size:
                    hole = i
                    break
        elif model == 'best':
            hole = min(
                (i for i, (base, sz) in enumerate(self.free_list) if sz >= size),
                default=None,
                key=lambda i: self.free_list[i][1]
            )
        elif model == 'worst':
            hole = max(
                (i for i, (base, sz) in enumerate(self.free_list) if sz >= size),
                default=None,
                key=lambda i: self.free_list[i][1]
            )
        elif model == 'circular':
            n = len(self.free_list)
            for offset in range(n):
                idx = (self._last_circular_index + offset) % n
                base, sz = self.free_list[idx]
                if sz >= size:
                    hole = idx
                    self._last_circular_index = idx
                    break
        if hole is None:
            return False
        base, sz = self.free_list[hole]
        self.allocated[pid] = Process(pid, size, base, size)
        if sz == size:
            new_free = self.free_list[:hole] + self.free_list[hole+1:]
        else:
            new_free = self.free_list[:hole] + [(base + size, sz - size)] + self.free_list[hole+1:]
        self.update_free_list(new_free)
        return True

    def remove_process(self, pid: int) -> bool:
        if pid not in self.allocated:
            return False
        block = self.allocated.pop(pid)
        new_free = self.free_list + [(block.base, block.limit)]
        self.update_free_list(new_free)
        return True

    def process_table(self) -> List[Process]:
        return list(self.allocated.values())

    def external_frag(self) -> float:
        free_total = sum(sz for (_, sz) in self.free_list)
        largest_hole = max((sz for (_, sz) in self.free_list), default=0)
        if free_total == 0:
            return 0.0
        return (free_total - largest_hole) / self.total_size * 100.0

    def simulated(self, granularity=1024) -> List[Optional[str]]:
        cells = [None] * (self.total_size // granularity)
        for pid, blk in self.allocated.items():
            start = blk.base // granularity
            end = (blk.base + blk.limit) // granularity
            for i in range(start, min(end, len(cells))):
                cells[i] = str(pid)
        return cells

# Alocador por Paginação

class Paginado:
    def __init__(self, total_frames: int, page_size: int):
        self.total_frames = total_frames
        self.page_size = page_size
        self.free_frames = list(range(total_frames))
        self.frame_owner: Dict[int, Tuple[int, int]] = {}
        self.page_tables: Dict[int, List[Pag]] = {}
        self.process_sizes: Dict[int, int] = {}

    def create_process(self, pid: int, size: int) -> bool:
        npages = math.ceil(size / self.page_size)
        if npages > len(self.free_frames):
            return False
        allocated_frames = [self.free_frames.pop(0) for _ in range(npages)]
        pte_list = []
        for pno, frame in enumerate(allocated_frames):
            self.frame_owner[frame] = (pid, pno)
            pte_list.append(Pag(pno, frame))
        self.page_tables[pid] = pte_list
        self.process_sizes[pid] = size
        return True

    def remove_process(self, pid: int) -> bool:
        if pid not in self.page_tables:
            return False
        for pte in self.page_tables[pid]:
            if pte.frame_number is not None:
                frame = pte.frame_number
                self.frame_owner.pop(frame, None)
                self.free_frames.append(frame)
        self.free_frames.sort()
        self.page_tables.pop(pid, None)
        self.process_sizes.pop(pid, None)
        return True

    def internal_frag(self) -> float:
        total_internal = 0
        for pid, size in self.process_sizes.items():
            pages = len(self.page_tables[pid])
            total_internal += pages * self.page_size - size
        return total_internal / (self.total_frames * self.page_size) * 100.0

    def simulated_frames(self) -> List[Optional[str]]:
        arr = [None] * self.total_frames
        for f in range(self.total_frames):
            if f in self.frame_owner:
                pid, page = self.frame_owner[f]
                arr[f] = f'{pid}:{page}'
        return arr

    def page_table_for(self, pid: int) -> List[Pag]:
        return self.page_tables.get(pid, [])

# Simulador da Interface

class MemorySimulator:
    def __init__(self, total_memory_bytes: int = 256*1024):
        self.total_memory = total_memory_bytes
        self.contiguous = Contiguo(total_memory_bytes)
        default_page = 4 * 1024
        self.default_frames = total_memory_bytes // default_page
        self.paging = Paginado(self.default_frames, default_page)
        self.next_pid = 1

    def run(self):
        while True:
            print('\nSimulador de Gerenciamento de Memória')
            print('1) Alocação Contígua Dinâmica')
            print('2) Paginação Pura')
            print('0) Sair')
            choice = input('> ').strip()
            if choice == '1':
                self._contiguous_menu()
            elif choice == '2':
                self._paging_menu()
            elif choice == '0':
                return

    def _contiguous_menu(self):
        model = 'first'
        while True:
            print('\nModo Contíguo')
            map(self.contiguous.simulated(granularity=2048), width=60)
            for blk in self.contiguous.process_table():
                print(f'PID {blk.pid} | Base {blk.base} | Limite {blk.limit}')
            print(f'Fragmentação externa: {self.contiguous.external_frag():.2f}%')
            print('\n1) Criar processo')
            print('2) Remover processo')
            print('3) Mudar algoritmo')
            print('0) Voltar')
            cmd = input('> ').strip()
            if cmd == '1':
                size = int(input('Tamanho do processo em bytes: '))
                pid = self.next_pid
                if self.contiguous.create_process(pid, size, model):
                    print(f'Processo {pid} criado')
                    self.next_pid += 1
                else:
                    print('Falha de alocação :(')
            elif cmd == '2':
                pid = int(input('PID: '))
                self.contiguous.remove_process(pid)
            elif cmd == '3':
                s = input('Algoritmo (first/best/worst/circular): ').strip()
                if s in ('first','best','worst','circular'):
                    model = s
            elif cmd == '0':
                return

    def _paging_menu(self):
        while True:
            print('\nModo Paginação')
            map(self.paging.simulated_frames(), width=60)
            for pid, size in self.paging.process_sizes.items():
                pages = len(self.paging.page_table_for(pid))
                print(f'PID {pid} | {size} bytes | {pages} páginas')
            print(f'Fragmentação interna: {self.paging.internal_frag():.2f}%\nFragmentação externa: 0% (ou equivalente, ela não se aplica em paginação)')
            print('\n1) Criar processo')
            print('2) Remover processo')
            print('3) Ver tabela de páginas')
            print('0) Voltar]')
            cmd = input('> ').strip()
            if cmd == '1':
                size = int(input('Tamanho do processo (bytes): '))
                pid = self.next_pid
                if self.paging.create_process(pid, size):
                    print(f'Processo {pid} criado')
                    self.next_pid += 1
                else:
                    print('Falha: frames insuficientes );')
            elif cmd == '2':
                pid = int(input('PID: '))
                self.paging.remove_process(pid)
            elif cmd == '3':
                pid = int(input('PID: '))
                for pte in self.paging.page_table_for(pid):
                    print(f'Página {pte.page_number} -> Frame {pte.frame_number}')
            elif cmd == '0':
                return

if __name__ == '__main__':
    sim = MemorySimulator()
    try:
        sim.run()
    except KeyboardInterrupt:
        sys.exit(0)