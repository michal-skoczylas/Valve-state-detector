<template>
  <div id="app-container">
    <EditModal 
      v-if="modalOpen" 
      :modalData="modalData" 
      @close="closeModal" 
      @save="saveModal" 
      @remove="removeModal"
    />

    <Sidebar 
      :configs="configs"
      :cameras="cameras"
      :images="images"
      :selectedConfig="selectedConfig"
      :selectedSource="selectedSource"
      :isRefreshing="isRefreshing"
      :params="params"
      @load-config="loadConfig"
      @save-config="saveConfig"
      @update:selectedSource="selectedSource = $event"
      @source-changed="sourceChanged"
      @refresh-cameras="refreshCameras"
      @clear-rois="clearRois"
      @update-visuals="updateVisuals"
    />

    <main class="main-content">
      <CameraView 
        :origImgSrc="origImgSrc"
        :threshImgSrc="threshImgSrc"
        :rois="rois"
        :highlightedIndex="highlightedIndex"
        :editingIndex="editingIndex"
        :selectedSource="selectedSource"
        @add-roi="addRoi"
        @pixel-click="handlePixelClick"
      />

      <ValveDashboard 
        :valves="valves"
        :highlightedIndex="highlightedIndex"
        @toggle-highlight="toggleHighlight"
        @edit="openModal"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import Sidebar from './components/Sidebar.vue'
import CameraView from './components/CameraView.vue'
import ValveDashboard from './components/ValveDashboard.vue'
import EditModal from './components/EditModal.vue'

const images = ref([])
const cameras = ref([])
const configs = ref([])

const selectedSource = ref('')
const selectedConfig = ref('')
const isRefreshing = ref(false)

const params = reactive({ h: 0, s: 0, v: 0, tol: 20, morphOn: false, morph: 0, minFill: 5 })
const rois = ref([])
const valves = ref([])

const origImgSrc = ref('')
const threshImgSrc = ref('')

const modalOpen = ref(false)
const editingIndex = ref(-1)
const highlightedIndex = ref(-1)
const modalData = reactive({ name: '', desc: '', baseState: 'yellow_is_open' })

let pollInterval = null

onMounted(async () => {
  try {
    const res = await axios.get('/api/init')
    images.value = res.data.images || []
    cameras.value = res.data.cameras || []
    fetchConfigs()
  } catch (err) {
    console.error("Failed to init", err)
  }
})

onUnmounted(() => {
  stopPolling()
})

const fetchConfigs = async () => {
  const res = await axios.get('/configs')
  configs.value = res.data
}

const toggleHighlight = (idx) => {
  highlightedIndex.value = highlightedIndex.value === idx ? -1 : idx
}

const refreshCameras = async () => {
  isRefreshing.value = true
  try {
    const res = await axios.get('/refresh_cameras')
    cameras.value = res.data
  } catch (e) {
    alert("Błąd skanowania kamer.")
  }
  isRefreshing.value = false
}

const saveConfig = async (newName) => {
  if (!newName.trim()) return alert("Podaj nazwę profilu!")
  const payload = {
    name: newName,
    ...params,
    rois: rois.value
  }
  await axios.post('/save_config', payload)
  fetchConfigs()
}

const loadConfig = async (cfg) => {
  if (!cfg) return alert("Wybierz profil z listy!")
  selectedConfig.value = cfg
  try {
    const res = await axios.get('/load_config/' + cfg)
    const data = res.data
    if (data.error) return alert("Błąd wczytywania.")
    
    Object.assign(params, {
      h: data.h || 0, s: data.s || 0, v: data.v || 0,
      tol: data.tol || 20, morphOn: data.morphOn || false,
      morph: data.morph || 0, minFill: data.minFill || 5
    })
    rois.value = data.rois || []
    highlightedIndex.value = -1
    updateVisuals()
  } catch(e) {
    alert("Błąd wczytywania configa")
  }
}

const sourceChanged = () => {
  if (!selectedSource.value) return
  stopPolling()
  highlightedIndex.value = -1

  if (selectedSource.value.startsWith('CAM_')) {
    const camId = selectedSource.value.replace('CAM_', '')
    axios.post(`/set_camera/${camId}`)
    
    origImgSrc.value = '/video_original'
    threshImgSrc.value = '/video_threshold'
    
    updateBackendParams()
    if (canAnalyze()) {
      pollInterval = setInterval(fetchAnalysisLive, 500)
    } else {
      valves.value = []
    }
  } else {
    axios.post('/set_camera/-1')
    origImgSrc.value = '/image/' + selectedSource.value
    updateVisuals()
  }
}

const updateVisuals = async () => {
  if (!selectedSource.value) return

  if (selectedSource.value.startsWith('CAM_')) {
    updateBackendParams()
    if (canAnalyze() && !pollInterval) {
      pollInterval = setInterval(fetchAnalysisLive, 500)
    } else if (!canAnalyze()) {
      stopPolling()
      valves.value = []
    }
  } else {
    if (!canAnalyze()) {
      threshImgSrc.value = origImgSrc.value
      valves.value = []
    } else {
      const urlParams = buildUrlParams()
      threshImgSrc.value = `/threshold/${selectedSource.value}?${urlParams}&t=${new Date().getTime()}`
      const res = await axios.get(`/analyze_valves/${selectedSource.value}?${urlParams}`)
      valves.value = res.data
    }
  }
}

const updateBackendParams = () => {
  axios.post('/update_cam_params', {
    h: params.h, tol: parseInt(params.tol),
    morph_on: params.morphOn, morph: parseInt(params.morph),
    min_fill: parseFloat(params.minFill), rois: rois.value
  })
}

const fetchAnalysisLive = async () => {
  try {
    const res = await axios.get('/camera_analyze')
    valves.value = res.data
  } catch (e) {}
}

const canAnalyze = () => {
  return (params.h > 0 && rois.value.length > 0)
}

const buildUrlParams = () => {
  const rJson = encodeURIComponent(JSON.stringify(rois.value))
  return `h=${params.h}&tol=${params.tol}&morph=${params.morph}&morph_on=${params.morphOn}&min_fill=${params.minFill}&rois=${rJson}`
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

const clearRois = () => {
  rois.value = []
  highlightedIndex.value = -1
  updateVisuals()
}

const addRoi = (roiData) => {
  rois.value.push(roiData)
  updateVisuals()
}

const handlePixelClick = async ({x, y}) => {
  const url = selectedSource.value.startsWith('CAM_')
    ? `/camera_pixel_value?x=${x}&y=${y}`
    : `/pixel_value/${selectedSource.value}?x=${x}&y=${y}`
    
  try {
    const res = await axios.get(url)
    params.h = res.data.h
    params.s = res.data.s
    params.v = res.data.v
    updateVisuals()
  } catch (e) {
    console.error(e)
  }
}

const openModal = (idx) => {
  editingIndex.value = idx
  const r = rois.value[idx]
  modalData.name = r.name
  modalData.desc = r.desc
  modalData.baseState = r.baseState
  modalOpen.value = true
}

const closeModal = () => {
  modalOpen.value = false
  editingIndex.value = -1
}

const saveModal = (data) => {
  if (editingIndex.value > -1) {
    rois.value[editingIndex.value].name = data.name
    rois.value[editingIndex.value].desc = data.desc
    rois.value[editingIndex.value].baseState = data.baseState
    updateVisuals()
  }
  closeModal()
}

const removeModal = () => {
  if (editingIndex.value > -1) {
    rois.value.splice(editingIndex.value, 1)
    updateVisuals()
  }
  closeModal()
}
</script>

<style scoped>
#app-container {
    display: flex;
    height: 100vh;
    width: 100%;
    overflow: hidden;
}

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding: 24px;
    gap: 24px;
}
</style>
