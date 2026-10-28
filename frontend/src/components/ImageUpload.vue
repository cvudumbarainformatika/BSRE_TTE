<script setup lang="ts">
import { ref, watch, computed } from "vue"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { X } from "lucide-vue-next"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

type ExistingImage = {
  id: number
  thumbnail: string
}

type ImageItem = {
  id: number | string;
  src: string;
  type: "existing" | "new";
  file?: File; // Store the file object for new images
}

const props = defineProps<{
  modelValue?: File[]
  existingImages?: ExistingImage[]
}>()

const emit = defineEmits<{
  (e: "update:modelValue", value: File[]): void
  (e: "remove-existing", id: number): void
}>()

const newFiles = ref<File[]>(props.modelValue || [])
const imagePreviews = ref<ImageItem[]>([])

const showConfirmDialog = ref(false)
const imageToRemove = ref<ImageItem | null>(null)

// Sync modelValue with newFiles and emit updates
watch(newFiles, (val) => {
  emit("update:modelValue", val)
}, { deep: true })


// Watch for changes in existing images (e.g., when loading an item to edit)
watch(
  () => props.existingImages,
  (newVal, oldVal) => {
    // Clear all existing previews first to handle removals/updates cleanly
    imagePreviews.value = imagePreviews.value.filter(p => p.type !== 'existing');

    if (newVal && newVal.length > 0) {
      const existingPreviews = newVal.map((img) => ({
        id: img.id,
        src: img.thumbnail, // Gunakan path langsung dari backend
        type: "existing" as const,
      }))
      // Add the updated list of existing previews
      imagePreviews.value.unshift(...existingPreviews);
    }
  },
  { immediate: true, deep: true }
)

const onSelectFiles = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files) return

  for (const file of Array.from(input.files)) {
    if (!file.type.startsWith("image/")) continue
    
    const newFileItem: ImageItem = {
      id: `new-${Date.now()}-${file.name}`,
      src: URL.createObjectURL(file),
      type: "new",
      file: file,
    };

    imagePreviews.value.push(newFileItem);
    newFiles.value.push(file);
  }

  input.value = "" // Clear input to allow selecting the same file again
}

const removeImage = (item: ImageItem) => {
  if (item.type === "existing") {
    imageToRemove.value = item
    showConfirmDialog.value = true
  } else {
    // This is a new file, remove it
    const indexToRemove = imagePreviews.value.findIndex(p => p.id === item.id)
    if (indexToRemove > -1) {
      const previewToRemove = imagePreviews.value[indexToRemove];
      URL.revokeObjectURL(previewToRemove.src)
      imagePreviews.value.splice(indexToRemove, 1)

      // Also remove from newFiles array
      const fileIndexToRemove = newFiles.value.findIndex(f => f === previewToRemove.file);
      if (fileIndexToRemove > -1) {
        newFiles.value.splice(fileIndexToRemove, 1);
      }
    }
  }
}

const confirmRemoval = () => {
  if (imageToRemove.value && imageToRemove.value.type === "existing") {
    emit("remove-existing", imageToRemove.value.id as number)
    imagePreviews.value = imagePreviews.value.filter(p => p.id !== imageToRemove.value?.id)
  }
  showConfirmDialog.value = false
  imageToRemove.value = null
}

const cancelRemoval = () => {
  showConfirmDialog.value = false
  imageToRemove.value = null
}
</script>

<template>
  <div class="space-y-4">
    <!-- File Input -->
    <Input
      type="file"
      accept="image/*"
      multiple
      @change="onSelectFiles"
    />

    <!-- Preview Grid -->
    <div
      v-if="imagePreviews.length"
      class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4"
    >
      <div
        v-for="img in imagePreviews"
        :key="img.id"
        class="relative group border rounded-lg overflow-hidden"
      >
        <img
          :src="img.src"
          class="h-32 w-full object-cover"
        />

        <!-- Remove Button -->
        <Button
          size="icon"
          variant="destructive"
          class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition"
          @click="removeImage(img)"
        >
          <X class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <AlertDialog :open="showConfirmDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Konfirmasi Penghapusan Gambar</AlertDialogTitle>
          <AlertDialogDescription>
            Apakah Anda yakin ingin menghapus gambar ini secara permanen dari server? Tindakan ini tidak dapat dibatalkan.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="cancelRemoval">Batal</AlertDialogCancel>
          <AlertDialogAction @click="confirmRemoval" class="bg-destructive text-destructive-foreground hover:bg-destructive/90">Hapus</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
