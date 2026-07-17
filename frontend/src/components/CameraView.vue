<template>
  <section class="camera-grid">
    <div class="panel">
      <h3>Oryginał (Konfiguracja ROI)</h3>
      <div class="img-container" ref="imgContainer" @mousedown="startDraw" @mousemove="onDraw" @mouseup="endDraw">
        <img :src="origImgSrc" alt="Brak źródła" @load="calculateScale" ref="origImg" ondragstart="return false;">

        <div v-for="(roi, idx) in rois" :key="idx" class="selection-box"
             :class="{'editing-box': idx === editingIndex, 'highlighted-box': idx === highlightedIndex}"
             :style="getRoiStyle(roi)">
        </div>

        <div v-if="isDrawing" class="selection-box"
             :style="{ left: drawBox.x + 'px', top: drawBox.y + 'px', width: drawBox.w + 'px', height: drawBox.h + 'px' }">
        </div>
      </div>
    </div>

    <div class="panel">
      <h3>Podgląd Maski Wizyjnej</h3>
      <div class="img-container">
        <img :src="threshImgSrc" alt="Maska wizyjna">
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  origImgSrc: String,
  threshImgSrc: String,
  rois: Array,
  highlightedIndex: Number,
  editingIndex: Number,
  selectedSource: String
})

const emit = defineEmits(['add-roi', 'pixel-click'])

const imgContainer = ref(null)
const origImg = ref(null)

const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
const drawBox = ref({ x: 0, y: 0, w: 0, h: 0 })
const scaleX = ref(1)
const scaleY = ref(1)

const calculateScale = () => {
  const img = origImg.value
  if (img && img.naturalWidth) {
    scaleX.value = img.width / img.naturalWidth
    scaleY.value = img.height / img.naturalHeight
  }
}

const getRoiStyle = (r) => {
  return {
    left: (r.rx * scaleX.value) + 'px', 
    top: (r.ry * scaleY.value) + 'px',
    width: (r.rw * scaleX.value) + 'px', 
    height: (r.rh * scaleY.value) + 'px'
  }
}

const startDraw = (e) => {
  const rect = imgContainer.value.getBoundingClientRect()
  startX.value = e.clientX - rect.left
  startY.value = e.clientY - rect.top
  isDrawing.value = true
  drawBox.value = { x: startX.value, y: startY.value, w: 0, h: 0 }
}

const onDraw = (e) => {
  if (!isDrawing.value) return
  const rect = imgContainer.value.getBoundingClientRect()
  const curX = e.clientX - rect.left
  const curY = e.clientY - rect.top
  drawBox.value.x = Math.min(startX.value, curX)
  drawBox.value.y = Math.min(startY.value, curY)
  drawBox.value.w = Math.abs(curX - startX.value)
  drawBox.value.h = Math.abs(curY - startY.value)
}

const endDraw = (e) => {
  if (!isDrawing.value) return
  isDrawing.value = false

  if (!props.selectedSource) return alert("Wybierz najpierw źródło obrazu z listy!")

  const rect = imgContainer.value.getBoundingClientRect()
  const endX = e.clientX - rect.left
  const endY = e.clientY - rect.top
  const w = Math.abs(endX - startX.value)
  const h = Math.abs(endY - startY.value)

  calculateScale()

  if (w < 5 && h < 5) {
    const clickX = Math.round(endX / scaleX.value)
    const clickY = Math.round(endY / scaleY.value)
    emit('pixel-click', { x: clickX, y: clickY })
  } else {
    emit('add-roi', {
      rx: Math.round(Math.min(startX.value, endX) / scaleX.value),
      ry: Math.round(Math.min(startY.value, endY) / scaleY.value),
      rw: Math.round(w / scaleX.value),
      rh: Math.round(h / scaleY.value),
      name: `ZAWÓR ${props.rois.length + 1}`,
      desc: '',
      baseState: 'yellow_is_open'
    })
  }
}

onMounted(() => {
  window.addEventListener('resize', calculateScale)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateScale)
})
</script>

<style scoped>
.camera-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

.img-container {
    position: relative;
    display: inline-block;
    user-select: none;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #1e293b;
    text-align: center;
    width: 100%;
    min-height: 200px;
}

.img-container img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
    cursor: crosshair;
}

.selection-box {
    position: absolute;
    border: 2px dashed #ffeb3b;
    background: rgba(255, 235, 59, 0.2);
    pointer-events: none;
    transition: all 0.2s;
}

.selection-box.editing-box {
    border: 3px solid #00d2ff;
    background: rgba(0, 210, 255, 0.3);
    box-shadow: 0 0 15px #00d2ff;
    z-index: 5;
}

.selection-box.highlighted-box {
    border: 3px solid var(--highlight);
    background: rgba(245, 158, 11, 0.4);
    box-shadow: 0 0 20px var(--highlight);
    z-index: 6;
}
</style>
