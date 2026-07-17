<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Edytuj Zawór</h3>
      <label>Nazwa (np. Zawór Główny)</label>
      <input type="text" v-model="localData.name">

      <label>Opis / Lokalizacja (Opcjonalnie)</label>
      <input type="text" v-model="localData.desc">

      <label>Logika działania strefy</label>
      <select v-model="localData.baseState">
        <option value="yellow_is_open">Kolor = OTWARTY (NO)</option>
        <option value="yellow_is_closed">Kolor = ZAMKNIĘTY (NC)</option>
      </select>

      <div class="modal-footer">
        <button class="btn-danger" style="width: auto; margin-right: auto; margin-top: 0;" @click="$emit('remove')">Usuń</button>
        <button class="btn-outline" style="width: auto;" @click="$emit('close')">Anuluj</button>
        <button class="btn-success" style="width: auto;" @click="$emit('save', localData)">Zapisz</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  modalData: Object
})

const emit = defineEmits(['close', 'save', 'remove'])

const localData = reactive({
  name: props.modalData.name,
  desc: props.modalData.desc,
  baseState: props.modalData.baseState
})

watch(() => props.modalData, (newData) => {
  localData.name = newData.name
  localData.desc = newData.desc
  localData.baseState = newData.baseState
}, { deep: true })
</script>
