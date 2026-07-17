<template>
  <aside class="sidebar">
    <div class="brand">Valve detector</div>

    <div class="control-group">
      <h4>Zarządzanie Konfiguracją</h4>
      <div class="flex-row">
        <select v-model="localSelectedConfig">
          <option value="">Wybierz profil...</option>
          <option v-for="cfg in configs" :key="cfg" :value="cfg">{{ cfg.replace('.json', '') }}</option>
        </select>
        <button class="btn-primary" style="width: auto; padding: 10px 15px;" @click="$emit('load-config', localSelectedConfig)">Wczytaj</button>
      </div>
      <div class="flex-row">
        <input type="text" v-model="newConfigName" placeholder="Nazwa profilu">
        <button class="btn-success" style="width: auto; padding: 10px 15px;" @click="$emit('save-config', newConfigName); newConfigName=''">Zapisz</button>
      </div>
    </div>

    <div class="control-group">
      <h4>Źródło Obrazu</h4>
      <div class="flex-row" style="margin-bottom: 0;">
        <select :value="selectedSource" @change="onSourceChange">
          <option value="" disabled>Wybierz źródło...</option>
          <optgroup label="Kamery (Na żywo)">
            <option v-for="cam in cameras" :key="'cam'+cam" :value="'CAM_' + cam" style="color: #ef4444; font-weight:bold;">
              🔴 Kamera {{ cam }}
            </option>
            <option v-if="cameras.length === 0" disabled>Brak podłączonych kamer</option>
          </optgroup>
          <optgroup label="Zapisane obrazy">
            <option v-for="img in images" :key="img" :value="img">📄 {{ img }}</option>
          </optgroup>
        </select>
        <button class="btn-primary" style="width: auto; padding: 10px 15px;" @click="$emit('refresh-cameras')" :disabled="isRefreshing">
          {{ isRefreshing ? '⏳' : '🔄' }}
        </button>
      </div>
      <button class="btn-danger" @click="$emit('clear-rois')">Wyczyść strefy</button>
    </div>

    <div class="control-group">
      <h4>Detekcja Koloru</h4>
      <label>Tolerancja barwy <span class="value-badge">{{ params.tol }}</span></label>
      <input type="range" v-model.number="params.tol" min="1" max="100" @input="$emit('update-visuals')">
    </div>

    <div class="control-group">
      <h4>Filtrowanie</h4>
      <label class="checkbox-wrapper">
        <input type="checkbox" v-model="params.morphOn" @change="$emit('update-visuals')"> Włącz wygładzanie
      </label>
      <label>Siła (Morfologia) <span class="value-badge">{{ params.morph }}</span></label>
      <input type="range" v-model.number="params.morph" min="0" max="35" :disabled="!params.morphOn" @input="$emit('update-visuals')">
    </div>

    <div class="control-group">
      <h4>Logika Detekcji</h4>
      <label>Wymagane pokrycie <span class="value-badge">{{ params.minFill }}%</span></label>
      <input type="range" v-model.number="params.minFill" min="1" max="100" @input="$emit('update-visuals')">
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  configs: Array,
  cameras: Array,
  images: Array,
  selectedConfig: String,
  selectedSource: String,
  isRefreshing: Boolean,
  params: Object
})

const emit = defineEmits(['load-config', 'save-config', 'update:selectedSource', 'source-changed', 'refresh-cameras', 'clear-rois', 'update-visuals'])

const localSelectedConfig = ref(props.selectedConfig || '')
const newConfigName = ref('')

const onSourceChange = (e) => {
  emit('update:selectedSource', e.target.value)
  emit('source-changed')
}
</script>

<style scoped>
.sidebar {
    width: 340px;
    background-color: var(--bg-panel);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding: 24px;
    z-index: 10;
    box-shadow: 4px 0 15px rgba(0, 0, 0, 0.03);
}

.brand {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    background-color: var(--success);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--success);
}

.control-group {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.control-group:last-child {
    border-bottom: none;
}

.control-group h4 {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
}
</style>
