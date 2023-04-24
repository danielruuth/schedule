<script setup>
import {ref} from 'vue'
import { useDialog } from 'primevue/usedialog';
import RulesModal from '../views/modals/rulesView.vue'
const dialog = useDialog()

const emit = defineEmits(['UpdateRules'])

const props = defineProps({
  rules: Object,
  shifts: Array
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
            rules:internalRules || {},
            shifts: props.shifts
        },
        emits: {
            onUpdateRules: (e) => {
                console.log('Emitting', e)
                internalRules.value = e
                //LEts bubble it
                emit('UpdateRules', {'health': e.health, 'min_weekends': e.min_weekends, 'group_offshift': e.group_offshift})
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12 item-start">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Regler: </span><br />
            <div class="text-xs font-thin" v-if="internalRules.health">Hälsoschema</div> 
            <div class="text-xs font-thin" v-if="internalRules.min_weekends">Gruppera helgpass</div> 
            <div class="text-xs font-thin" v-if="internalRules.group_offshift">Sammanhållen ledighet</div> 
        </div>
        <div class="col-span-1 justify-self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event)"></span>
        </div>
    </div>
</template>