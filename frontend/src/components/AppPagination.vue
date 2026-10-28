<template>
  <Pagination
    :items-per-page="meta?.per_page ?? 10"
    :total="meta?.total ?? 0"
    :default-page="modelValue ?? 1"
    @update:page="onPageChange"
  >
    <PaginationContent class="flex items-center gap-1 text-stone-700 dark:text-white">

      <!-- FIRST -->
      <PaginationFirst
        :disabled="modelValue <= 1"
        @click="goTo(1)"
        class="btn"
      >
        <ChevronsLeft class="icon" />
      </PaginationFirst>

      <!-- PREV -->
      <PaginationPrevious
        :disabled="modelValue <= 1"
        @click="goTo(modelValue - 1)"
        class="btn mr-2"
      >
        <ChevronLeft class="icon" />
      </PaginationPrevious>

      <!-- PAGE LIST -->
      <template v-for="(item, index) in displayPages" :key="index">
        <PaginationItem
          v-if="item !== '...'"
          :value="item"
          @click="goTo(item)"
          class="!w-8 !h-8 !text-xs border border-border bg-muted/50 text-muted-foreground rounded-md
       data-[selected]:bg-primary data-[selected]:text-primary-foreground
       hover:bg-accent hover:text-accent-foreground
       transition cursor-pointer"
          :class="[
            item === modelValue ? 'active' : ''
          ]"
        >
          {{ item }}
        </PaginationItem>

        <PaginationEllipsis v-else class="w-7 h-7 flex items-center justify-center">
          &#8230;
        </PaginationEllipsis>
      </template>

      <!-- NEXT -->
      <PaginationNext
        :disabled="modelValue >= lastPage"
        @click="goTo(modelValue + 1)"
        class="btn ml-2"
      >
        <ChevronRight class="icon" />
      </PaginationNext>

      <!-- LAST -->
      <PaginationLast
        :disabled="modelValue >= lastPage"
        @click="goTo(lastPage)"
        class="btn"
      >
        <ChevronsRight class="icon" />
      </PaginationLast>
    </PaginationContent>
  </Pagination>
</template>

<script setup>
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationFirst,
  PaginationPrevious,
  PaginationEllipsis,
  PaginationNext,
  PaginationLast
} from '@/components/ui/pagination'

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 1 },
  meta: { type: Object, required: true },
  maxVisiblePages: { type: Number, default: 5 } // ⬅️ custom control
})

const emit = defineEmits(['update:modelValue', 'change'])

const lastPage = computed(() => {
  const total = props.meta?.total ?? 0
  const perPage = props.meta?.per_page ?? 10
  return Math.max(1, Math.ceil(total / perPage))
})

/*  ---- Smart Pagination Builder (GitHub style) ----  */
const displayPages = computed(() => {
  const total = lastPage.value
  const current = props.modelValue
  const max = props.maxVisiblePages

  if (total <= max + 2) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages = [1]

  const start = Math.max(2, current - Math.floor(max / 2))
  const end = Math.min(total - 1, current + Math.floor(max / 2))

  if (start > 2) pages.push("...")

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (end < total - 1) pages.push("...")

  pages.push(total)

  return pages
})

function goTo(page) {
  if (page < 1 || page > lastPage.value) return
  emit('update:modelValue', page)
  emit('change', page)
}

function onPageChange(page) {
  goTo(page)
}
</script>

<style scoped>
</style>
