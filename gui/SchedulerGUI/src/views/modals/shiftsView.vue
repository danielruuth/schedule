<script setup>
    import {ref, inject, computed} from 'vue'
   
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['onAddedShift'])

    const weekdays = ref([
        'Måndag',
        'Tisdag',
        'Onsdag',
        'Torsdag',
        'Fredag',
        'Lördag',
        'Söndag'
    ])

    const shift_titles = [
        'Dag (A)',
        'Kväll (C)',
        'Natt',
        'Annat (?)'
    ]

    const number_shifts = ref(dialogRef.value.data.shifts[0].length || 2)

    const updateShiftCount = function(){
        for(let i = 0; i <= 6; i++){
        for(let n = 0; n < number_shifts.value; n++){
                if(!shifts_counts_array.value[i][n]){
                    shifts_counts_array.value[i][n] = 0;
                }else if(shifts_counts_array.value[i].length > number_shifts.value){
                    shifts_counts_array.value[i].splice(0, shifts_counts_array.value[i].length-number_shifts.value)
                }
            }
        }
    }

    const shifts_counts_array = ref(dialogRef.value.data.shifts || [
        [], //mo
        [], //tu
        [], //we
        [], //th
        [], //fr
        [], //sa
        []  //su
    ])

    const saveAndUpdate = function(){
        emit('AddedShift', shifts_counts_array)
        dialogRef.value.close()
    }

</script>
<template>
    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-10">
            <span class="text-xs font-bold uppercase">Antal skift per dag </span><small class="text-xs font-light">t.ex 2</small>
            <input type="number" v-model="number_shifts" class="form-input rounded-md bg-gray-100 border-transparent w-full" @change="updateShiftCount"/>
        </div>
        <div class="col-span-10 ">
            <span class="text-xs font-bold uppercase">Antal resurser per dag och skift </span>
            <div v-for="n in 7" class="gap-2 mt-4">
                <span class="text-sm font-bold uppercase">{{ weekdays[n-1] }}</span>
                <div :class="'mt-2 grid gap-2 grid-cols-' + number_shifts">
                    <div v-for="i in number_shifts" class="col-span-1">
                    
                        <span class="text-xs font-bold uppercase">{{ shift_titles[i-1] }}</span>
                        <input type="number" v-model="shifts_counts_array[n-1][i-1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                        
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-span-10">
            <Button label="Spara" class="w-full float-right" style="height:42px" @click="saveAndUpdate()" />
        </div>
        
    </div>
</template>