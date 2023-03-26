<script setup>
    import {ref, inject} from 'vue'
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['UpdateRules'])

    console.log(dialogRef.value.data.rules.health)

    const health = ref(dialogRef.value.data.rules.health || false)
    const weekendsConcat = ref(dialogRef.value.data.rules.min_weekends || false)

    const updateSettings = function(event){
        console.log('Updating rules')
        emit('UpdateRules', {'health': health, 'min_weekends': weekendsConcat})
    }

</script>
<template>
    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Används hälsoschema </span><br />
            <span class="text-xs font-light">Sätt regler efter hälsoschema-modellen, läs mer <a href="#">här</a>.</span><br />
            <InputSwitch class="mt-4" v-model="health" @change="updateSettings($event)"/>
        </div>
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Gruppera helgpass</span><br />
            <span class="text-xs font-light">Används samma resurser för fredagkväll, lördag och söndagspass.</span><br />
            <InputSwitch class="mt-4" v-model="weekendsConcat" @change="updateSettings($event)" />
        </div>
    </div>
</template>