<script setup>
import {ref} from 'vue'
import { useDialog } from 'primevue/usedialog';
import RulesModal from '../views/modals/rulesView.vue'
const dialog = useDialog()

const props = defineProps({
  rules: Object
})

const internalRules = ref(props.rules)

const openModal = function(event, view){
    dialog.open(RulesModal, {
        props:{
            style: {
                width: '50vw'
            },
        },
        data:{
            rules:internalRules || {}
        },
        emits: {
            onUpdateRules: (e) => {
                console.log('Emitting', e)
                internalRules.value = e
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Regler: </span>
            <span class="text-xs font-thin" v-if="internalRules.health">Hälsoschema</span> 
            <span class="text-xs font-thin" v-if="internalRules.min_weekends">Gruppera helgpass</span> 
        </div>
        <div class="col-span-1 self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event)"></span>
        </div>
    </div>
</template>