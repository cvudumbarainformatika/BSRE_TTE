<script setup>
import { ref, computed, watch } from 'vue'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Search, 
  ChevronLeft, 
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Loader2
} from 'lucide-vue-next'

const props = defineProps({
  title: String,
  description: String,
  items: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  loading: Boolean,
  pageSize: { type: Number, default: 10 },
  searchPlaceholder: { type: String, default: 'Cari data...' },
  showAddButton: { type: Boolean, default: true },
  addButtonLabel: { type: String, default: 'Tambah Data' },
  serverSide: { type: Boolean, default: false },
  totalItems: { type: Number, default: 0 }
})

const emit = defineEmits(['add', 'rowClick', 'change'])

const searchQuery = ref('')
const currentPage = ref(1)

const filteredItems = computed(() => {
  if (props.serverSide) return props.items || []

  let result = props.items || []
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(item => {
      return Object.values(item).some(val => 
        String(val).toLowerCase().includes(q)
      )
    })
  }
  
  return result
})

// --- Pagination Logic ---
const totalDataCount = computed(() => props.serverSide ? props.totalItems : filteredItems.value.length)
const totalPages = computed(() => Math.ceil(totalDataCount.value / props.pageSize) || 1)

const startItem = computed(() => totalDataCount.value === 0 ? 0 : (currentPage.value - 1) * props.pageSize + 1)
const endItem = computed(() => Math.min(currentPage.value * props.pageSize, totalDataCount.value))

const visiblePages = computed(() => {
  const delta = 1 // Jumlah halaman di kiri-kanan halaman aktif
  const range = []
  const pages = []

  for (let i = Math.max(2, currentPage.value - delta); i <= Math.min(totalPages.value - 1, currentPage.value + delta); i++) {
    range.push(i)
  }

  if (currentPage.value - delta > 2) pages.push(1, '...')
  else pages.push(1)

  pages.push(...range)

  if (currentPage.value + delta < totalPages.value - 1) pages.push('...', totalPages.value)
  else if (totalPages.value > 1) pages.push(totalPages.value)

  return pages
})

function goToPage(page) {
  if (page === '...' || page < 1 || page > totalPages.value) return
  currentPage.value = page
}

const paginatedItems = computed(() => {
  if (props.serverSide) return props.items || []
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredItems.value.slice(start, end)
})

// --- Server Side Emitter & Watchers ---
let debounceTimer = null

// Watch Search: Reset page and debounce emit
watch(searchQuery, (newSearch) => {
  if (!props.serverSide) return
  
  currentPage.value = 1
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('change', { page: 1, search: newSearch })
  }, 500)
})

// Watch Page: Emit immediately
watch(currentPage, (newPage) => {
  if (!props.serverSide) return
  emit('change', { page: newPage, search: searchQuery.value })
})

const handleRowClick = (item) => {
  emit('rowClick', item)
}
</script>

<template>
  <div class="data-table-premium-container space-y-4">
    <!-- Top Bar: Search & Custom Filters -->
    <Card class="border-none bg-card shadow-sm ring-1 ring-border overflow-hidden">
      <CardContent class="p-4 sm:p-6">
          <!-- Pencarian & Filter Grid -->
          <div class="w-full grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
            <!-- Search Bar (Standard) -->
            <div class="md:col-span-4 space-y-2 text-left">
              <Label class="text-[10px] font-bold uppercase text-muted-foreground flex items-center tracking-wider">
                <Search class="h-3 w-3 mr-1" /> Pencarian Cepat
              </Label>
              <div class="relative">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input 
                  v-model="searchQuery" 
                  :placeholder="searchPlaceholder" 
                  class="pl-9 h-10 bg-background border-border shadow-sm focus-visible:ring-primary/20 focus-visible:border-primary transition-all text-foreground"
                />
              </div>
            </div>

            <!-- Custom Filters Slot -->
            <div class="md:col-span-8">
              <div class="flex flex-wrap md:flex-nowrap gap-3 items-end justify-start md:justify-end">
                <slot name="filters" :handleFilterChange="() => currentPage = 1"></slot>
              </div>
            </div>
          </div>
      </CardContent>
    </Card>

    <!-- Main Table Card -->
    <Card class="overflow-hidden shadow-md border-border ring-1 ring-border">
      <CardHeader v-if="title" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b bg-background">
        <div class="space-y-1 text-left">
          <CardTitle class="text-xl font-bold tracking-tight text-foreground">{{ title }}</CardTitle>
          <CardDescription v-if="description" class="text-[11px] text-muted-foreground">{{ description }}</CardDescription>
        </div>
        <div class="w-full sm:w-auto flex items-center gap-2">
            <!-- Extra Actions Slot (Always visible if provided) -->
            <slot name="extra-actions"></slot>

            <div v-if="showAddButton">
                <slot name="add-button">
                    <Button size="sm" @click="emit('add')" class="w-full sm:w-auto shadow-sm">
                        <slot name="add-icon"></slot>
                        {{ addButtonLabel }}
                    </Button>
                </slot>
            </div>
        </div>
      </CardHeader>
      
      <CardContent class="p-0">
        <!-- Desktop Table View -->
        <div class="hidden md:block overflow-x-auto bg-card">
          <Table>
            <TableHeader>
              <TableRow class="bg-muted/50 hover:bg-muted/50 border-b-2 border-border">
                <TableHead v-for="col in columns" :key="col.key" :class="[col.align === 'right' ? 'text-right' : 'text-left', col.class, 'py-4 px-6 text-slate-900 font-bold uppercase text-[10px] sm:text-xs tracking-wider']">
                  {{ col.label }}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <!-- Loading State -->
              <TableRow v-if="loading">
                <TableCell :colspan="columns.length" class="h-32 text-center">
                  <Loader2 class="h-8 w-8 animate-spin mx-auto text-primary/40" />
                </TableCell>
              </TableRow>
              <!-- Empty State -->
              <TableRow v-else-if="filteredItems.length === 0">
                <TableCell :colspan="columns.length" class="h-32 text-center text-muted-foreground italic">
                  Tidak ada data yang ditemukan.
                </TableCell>
              </TableRow>
              <!-- Data Rows -->
              <TableRow 
                v-else
                v-for="item in paginatedItems" 
                :key="item.id || item.index"
                class="group transition-colors even:bg-muted/50 hover:bg-muted/40 cursor-pointer border-b border-border/40"
                @click="handleRowClick(item)"
              >
                <TableCell 
                    v-for="col in columns" 
                    :key="col.key" 
                    :class="[col.align === 'right' ? 'text-right' : 'text-left', col.class, 'py-3 px-6']"
                >
                  <div v-if="col.isAction" class="relative h-10 px-2 flex items-center justify-end overflow-hidden">
                      <div class="transition-all duration-300 opacity-100 group-hover:opacity-0 group-hover:pointer-events-none absolute right-2">
                        <slot :name="`cell-${col.key}`" :item="item">
                          {{ item[col.key] }}
                        </slot>
                      </div>
                      <div class="flex items-center gap-1 transition-all duration-300 opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 pointer-events-none group-hover:pointer-events-auto">
                         <slot name="actions" :item="item"></slot>
                      </div>
                  </div>
                  <div v-else :class="col.align === 'right' ? 'flex justify-end' : 'flex justify-start'">
                    <slot :name="`cell-${col.key}`" :item="item">
                      <span class="text-xs sm:text-sm">{{ item[col.key] }}</span>
                    </slot>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <!-- Mobile List View (Premium List Style) -->
        <div class="md:hidden divide-y divide-border/20 bg-card">
          <!-- Loading State -->
          <div v-if="loading" class="p-8 text-center">
            <Loader2 class="h-8 w-8 animate-spin mx-auto text-primary/40" />
          </div>
          <!-- Empty State -->
          <div v-else-if="filteredItems.length === 0" class="p-8 text-center text-muted-foreground italic text-sm">
            Tidak ada data yang ditemukan.
          </div>
          <!-- Card Items (Clean & Professional) -->
          <div 
            v-else
            v-for="item in paginatedItems" 
            :key="item.id || item.index"
            class="p-5 space-y-4 active:bg-muted/30 transition-colors"
            @click="handleRowClick(item)"
          >
            <!-- Header: Avatar/Initial + Name + Actions -->
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <slot :name="`cell-${columns[0].key}`" :item="item">
                  <span class="font-bold text-sm text-foreground">{{ item[columns[0].key] }}</span>
                </slot>
              </div>
              <!-- Actions: Compact & Always Visible -->
              <div class="flex items-center gap-1.5 shrink-0">
                <slot name="actions" :item="item"></slot>
              </div>
            </div>
            
            <!-- Details Area (No rigid labels) -->
            <div class="space-y-3">
               <div v-for="col in columns.slice(1, -2)" :key="col.key" class="text-left">
                  <slot :name="`cell-${col.key}`" :item="item">
                    <span class="text-xs text-muted-foreground">{{ item[col.key] }}</span>
                  </slot>
               </div>
            </div>

            <!-- Footer: Status & Date (Side by side) -->
            <div class="flex items-end justify-between pt-3 border-t border-border/10">
              <div class="flex flex-col gap-1">
                <!-- Status Column (Usually 2nd to last) -->
                <slot :name="`cell-${columns[columns.length - 2].key}`" :item="item">
                   <span class="text-[10px] font-bold uppercase text-muted-foreground">{{ item[columns[columns.length - 2].key] }}</span>
                </slot>
              </div>
              
              <div class="text-right">
                <!-- Date/Time Column (Last) -->
                <slot :name="`cell-${columns[columns.length - 1].key}`" :item="item">
                   <span class="text-[10px] text-muted-foreground">{{ item[columns[columns.length - 1].key] }}</span>
                </slot>
              </div>
            </div>
          </div>
        </div>

        <!-- Professional Pagination -->
        <div class="px-6 py-5 border-t border-border/50 bg-muted/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <!-- Pagination Info -->
          <div class="text-xs text-muted-foreground font-medium order-2 md:order-1 flex items-center">
            Menampilkan <span class="mx-1 text-foreground font-bold">{{ startItem }}</span> 
            sampai <span class="mx-1 text-foreground font-bold">{{ endItem }}</span> 
            dari <span class="mx-1 text-foreground font-bold">{{ totalDataCount }}</span> data
          </div>

          <!-- Pagination Controls -->
          <div class="flex items-center gap-1.5 order-1 md:order-2">
            <!-- First Page -->
            <Button
              variant="outline"
              size="icon"
              class="h-8 w-8 border-border/50 hover:bg-background hover:text-primary transition-all shadow-sm"
              :disabled="currentPage === 1"
              @click.stop="goToPage(1)"
            >
              <ChevronsLeft class="h-3.5 w-3.5" />
            </Button>

            <!-- Prev Page -->
            <Button
              variant="outline"
              size="icon"
              class="h-8 w-8 border-border/50 hover:bg-background hover:text-primary transition-all shadow-sm"
              :disabled="currentPage === 1"
              @click.stop="goToPage(currentPage - 1)"
            >
              <ChevronLeft class="h-3.5 w-3.5" />
            </Button>

            <!-- Page Numbers -->
            <div class="flex items-center gap-1 mx-1">
              <template v-for="(page, idx) in visiblePages" :key="idx">
                <Button
                  v-if="page !== '...'"
                  :variant="currentPage === page ? 'default' : 'outline'"
                  size="sm"
                  class="h-8 min-w-[32px] px-2 text-[11px] font-bold transition-all shadow-sm"
                  :class="currentPage === page ? 'bg-primary text-primary-foreground shadow-primary/20' : 'border-border/50 hover:bg-background hover:text-primary'"
                  @click.stop="goToPage(page)"
                >
                  {{ page }}
                </Button>
                <span v-else class="px-1 text-muted-foreground font-bold text-[10px]">...</span>
              </template>
            </div>

            <!-- Next Page -->
            <Button
              variant="outline"
              size="icon"
              class="h-8 w-8 border-border/50 hover:bg-background hover:text-primary transition-all shadow-sm"
              :disabled="currentPage === totalPages"
              @click.stop="goToPage(currentPage + 1)"
            >
              <ChevronRight class="h-3.5 w-3.5" />
            </Button>

            <!-- Last Page -->
            <Button
              variant="outline"
              size="icon"
              class="h-8 w-8 border-border/50 hover:bg-background hover:text-primary transition-all shadow-sm"
              :disabled="currentPage === totalPages"
              @click.stop="goToPage(totalPages)"
            >
              <ChevronsRight class="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<style scoped>
/* Standard Zebra & Hover is handled by Tailwind classes */
</style>
