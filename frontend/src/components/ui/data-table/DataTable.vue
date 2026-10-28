<template>
  <div class="w-full space-y-4">
    <!-- Header dengan filter dan tombol aksi -->
    <div class="flex flex-col md:flex-row items-start md:items-center gap-4">
      <!-- Input search -->
      <div class="mr-auto flex gap-2">
        <div v-if="searchable" class="relative min-w-[250px]">
          <InputGroup class="full-width">
            <InputGroupInput v-model="store.params.q" placeholder="Cari... (Enter)" @keyup.enter="onSearchChange"/>
            <InputGroupAddon>
              <SearchIcon />
            </InputGroupAddon>
            <InputGroupAddon align="inline-end" v-if="store.params.q" @click="onClearSearch" class="cursor-pointer">
              <XIcon />
            </InputGroupAddon>
          </InputGroup>
        </div>
        <slot name="other-filters" ></slot>
      </div>
      <div class="flex items-center gap-2">
          <!-- <span class="text-sm text-muted-foreground">Baris per halaman:</span> -->
        <div>
          <Select v-model="selectedPerPage" @update:model-value="onPerPageChange">
          <SelectTrigger >
            <SelectValue :placeholder="`${store.params.per_page}`" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="option in perPageOptions" :key="option" :value="option">
              {{ option }}
            </SelectItem>
          </SelectContent>
        </Select>
        </div>

        <!-- <slot name="actions" ></slot> -->
         <div class="flex gap-2">
          <TooltipApp label="Refresh Data">

            <Button variant="outline" size="icon" @click="onRefresh">
              <RefreshCwIcon class="h-4 w-4" />
            </Button>
          </TooltipApp>
          <TooltipApp label="Tambah Data Baru">
            <Button size="icon"  @click="onAdd">
              <PlusIcon class="h-4 w-4" />
            </Button>
          </TooltipApp>
         </div>
      </div>

      
    </div>

    <Card>
      <CardContent class="p-4">
         <!-- Tabel -->
        <div class="rounded-md border">
          <Table>
            <TableHeader >
              <TableRow>
                <TableHead v-for="column in columns" :key="column.key" :class="['bg-muted text-black dark:text-muted-foreground', column.align || '']">
                  <div class="flex items-center" :class="column.align === 'text-right' ? 'justify-end' : column.align === 'text-center' ? 'justify-center' : ''">
                    {{ column.label }}
                    <Button
                      v-if="column.sortable"
                      variant="ghost"
                      size="sm"
                      @click="onSortChange(column.key)"
                      class="ml-2 h-4 w-4"
                    >
                      <svg
                        v-if="store.params.order_by === column.key && store.params.sort === 'asc'"
                        class="h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M5 15l7-7 7 7"
                        />
                      </svg>
                      <svg
                        v-else-if="store.params.order_by === column.key && store.params.sort === 'desc'"
                        class="h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                      <svg
                        v-else
                        class="h-4 w-4 opacity-50"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                        />
                      </svg>
                    </Button>
                  </div>
                </TableHead>
                <TableHead class="text-right">
                  Aksi
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="(item, index) in store.items" :key="item.id" :class="store.loading ? 'opacity-50' : ''">
                <TableCell v-for="column in columns" :key="column.key" :class="column.align || ''">
                  <slot :name="column.key" :item="item" :value="item[column.key]" :index="index">
                    {{ item[column.key] || '-' }}
                  </slot>
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-1 w-full">
                    <TooltipApp label="Edit">
                       <Button variant="ghost" size="icon-sm" @click="onEdit(item)">
                        <EditIcon class="h-3 w-3 text-primary" />
                      </Button>
                    </TooltipApp>
                    <TooltipApp v-if="deleted" label="Hapus" >
                       <Button variant="ghost" size="icon-sm" @click="onDelete(item)">
                        <Loader2 v-if="store.deleting && store.loadingDeletes[index]" class="h-4 w-4 text-destructive animate-spin" />
                        <TrashIcon v-else class="h-3 w-3 text-destructive " />
                      </Button>
                    </TooltipApp>
                  </div>
                </TableCell>

              </TableRow>

             

              <!-- Loading skeleton -->
              <TableRow v-if="store.loading" v-for="i in 5" :key="'skeleton-' + i">
                <TableCell v-for="column in columns" :key="'skeleton-cell-' + column.key" :class="column.align || ''">
                  <div class="h-4 bg-gradient-to-r from-muted via-muted-foreground/10 to-muted rounded animate-shimmer bg-[length:200%_100%]"></div>
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-1">
                    <div class="h-8 w-8 bg-gradient-to-r from-muted via-muted-foreground/10 to-muted rounded animate-shimmer bg-[length:200%_100%]"></div>
                    <div class="h-8 w-8 bg-gradient-to-r from-muted via-muted-foreground/10 to-muted rounded animate-shimmer bg-[length:200%_100%]"></div>
                  </div>
                </TableCell>
              </TableRow>

              <!-- Empty state -->
              <TableRow v-if="!store.loading && store?.items?.length === 0" class="h-96">
                <TableCell :colspan="columns.length + 1" class="text-center">
                  <div class="py-16 text-center">
                    <!-- Futuristic empty state illustration -->
                    <div class="relative mx-auto w-64 h-64 mb-6">
                      <!-- Outer ring -->
                      <div class="absolute inset-0 rounded-full border-4 border-dashed border-muted-foreground/20 animate-spin-slow"></div>
                      <!-- Middle ring -->
                      <div class="absolute inset-8 rounded-full border-4 border-dotted border-primary/30 animate-spin-reverse"></div>
                      <!-- Inner circle with icon -->
                      <div class="absolute inset-16 rounded-full bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center">
                        <svg
                          class="h-20 w-20 text-muted-foreground/40"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="1.5"
                            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                          />
                        </svg>
                      </div>
                      <!-- Floating particles -->
                      <div class="absolute top-4 right-8 w-2 h-2 bg-primary/40 rounded-full animate-float"></div>
                      <div class="absolute bottom-8 left-4 w-3 h-3 bg-primary/30 rounded-full animate-float-delayed"></div>
                      <div class="absolute top-1/2 right-4 w-2 h-2 bg-primary/20 rounded-full animate-float-slow"></div>
                    </div>
                    
                    <h3 class="text-lg font-semibold text-foreground bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
                      {{ store.emptyData }}
                    </h3>
                    <p class="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
                      {{ store.emptyDataDesc }}
                    </p>
                    
                    <!-- Action hint -->
                    <div class="mt-6 flex items-center justify-center gap-2 text-xs text-muted-foreground">
                      <div class="flex items-center gap-1 px-3 py-1.5 rounded-full border border-dashed border-muted-foreground/30">
                        <PlusIcon class="h-3 w-3" />
                        <span>Klik tombol tambah untuk memulai</span>
                      </div>
                    </div>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <!-- Footer dengan pagination -->
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 pt-4">
          <!-- Jumlah data per halaman -->
          <div class="flex items-center gap-2">
            <div class="text-sm text-muted-foreground">
              Tampil
              <strong>{{ store.meta?.from ?? 0 }}</strong> -
              <strong>{{ store.meta?.to ?? 0 }}</strong> dari
              <strong>{{ store.meta?.total ?? 0 }}</strong> data
            </div>
            
          </div>

          <!-- Pagination controls -->
          <!-- <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="store.params.page <= 1"
              @click="store.setPage(1)"
            >
              <svg
                class="h-4 w-4 mr-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
                />
              </svg>
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="store.params.page <= 1"
              @click="store.setPage(store.params.page - 1)"
            >
              <svg
                class="h-4 w-4 mr-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </Button>

            <div class="flex items-center gap-1">
              <Button
                v-if="startPage > 1"
                variant="outline"
                size="sm"
                @click="store.setPage(1)"
              >
                1
              </Button>
              <span v-if="startPage > 2" class="text-sm">...</span>

              <Button
                v-for="page in visiblePages"
                :key="page"
                :variant="store.params.page === page ? 'default' : 'outline'"
                size="sm"
                @click="store.setPage(page)"
              >
                {{ page }}
              </Button>

              <span v-if="endPage < store.meta?.last_page - 1" class="text-sm">...</span>
              <Button
                v-if="endPage < store.meta?.last_page"
                variant="outline"
                size="sm"
                @click="store.setPage(store.meta?.last_page)"
              >
                {{ store.meta?.last_page }}
              </Button>
            </div>

            <Button
              variant="outline"
              size="sm"
              :disabled="!store.hasMore || store.fetching"
              @click="store.setPage(store.params.page + 1)"
            >
              <svg
                class="h-4 w-4 mr-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="!store.hasMore || store.fetching"
              @click="store.setPage(store.meta?.last_page)"
            >
              <svg
                class="h-4 w-4 mr-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 5l7 7-7 7m-8-14l7 7-7 7"
                />
              </svg>
            </Button>
          </div> -->
          <div>
            <AppPagination
              v-if="store.meta"
              v-model="store.params.page"
              :meta="store.meta"
              @change="store.setPage"
            />
          </div>
        
        </div>
      </CardContent>
    </Card>

   
  </div>
</template>

<script setup>
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent } from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import { SearchIcon, XIcon, TrashIcon, PencilIcon, EditIcon, Loader2, PlusIcon, RefreshCwIcon } from 'lucide-vue-next'
import { InputGroup, InputGroupAddon, InputGroupInput } from '@/components/ui/input-group'
import TooltipApp from '@/components/TooltipApp.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import AppPagination from '@/components/AppPagination.vue'
import { computed, ref } from 'vue'

// Props
const props = defineProps({
  store: {
    type: Object,
    required: true
  },
  columns: {
    type: Array,
    required: true,
    default: () => []
  },
  searchable: {
    type: Boolean,
    default: true
  },
  deleted: {
    type: Boolean,
    default: true
  }
})

// Emit event
const emit = defineEmits(['add','edit', 'delete', 'refresh'])

// State untuk per page options
const perPageOptions = ref([5, 10, 15, 20, 25, 50])
const selectedPerPage = computed({
  get: () => props.store.params.per_page,
  set: (value) => {
    props.store.params.per_page = value;
  }
})

const totalPages = computed(() => {
  return Math.ceil(props.store.meta?.total / props.store.params.per_page) || 1
})

// Fungsi-fungsi
const onSearchChange = (value) => {
  // console.log('onSearchChange', value);
  const term = props.store.params.q
  props.store.setSearch(term)
}

const onClearSearch = () => {
  const term = ''
  props.store.setSearch(term)
}

const onPerPageChange = (value) => {
  props.store.params.per_page = value;
  props.store.params.page = 1; // Reset ke halaman pertama
  props.store.fetchAll();
}

const onSortChange = (key) => {
  const currentOrderBy = props.store.params.order_by
  const currentSort = props.store.params.sort
  let newSort = 'asc'

  if (currentOrderBy === key) {
    newSort = currentSort === 'asc' ? 'desc' : 'asc'
  }

  props.store.params.order_by = key
  props.store.params.sort = newSort
  props.store.fetchAll()
}

const onAdd = () => {
  emit('add')
}
const onEdit = (item) => {
  emit('edit', item)
}

const onDelete = (item) => {
  emit('delete', item)
}

const onRefresh = () => {
  emit('refresh')
  // props.store.fetchAll()
}

// Pagination logic
const visiblePages = computed(() => {
  const totalPages = props.store.meta?.last_page || 1
  const currentPage = props.store.params.page || 1
  const maxVisiblePages = 5

  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2))
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1)
  }

  const pages = []
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})

const startPage = computed(() => {
  return visiblePages.value[0]
})

const endPage = computed(() => {
  const pages = visiblePages.value
  return pages[pages.length - 1]
})
</script>