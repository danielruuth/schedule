<script setup>
    import {ref, inject} from 'vue'
    import moment from 'moment'
   
   const dialogRef = inject('dialogRef')
   const emit = defineEmits(['UpdatedDates'])

   const startDate = ref(dialogRef.value.data.startDate)
   const weeks = ref(dialogRef.value.data.weeks)

   const date = ref()

   const saveDateTime = function(){
        console.log('StartDate', startDate)
        emit('UpdatedDates', {'startDate': startDate, 'weeks': weeks})
        dialogRef.value.close()
   }

</script>
<template>
    <div class="grid gap-1 grid-cols-10 gap-x-2 gap-y-2">
        <div class="col-span-7">
            <span class="text-xs font-bold uppercase">Startdatum </span>
            <input type="date" v-model="startDate" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div class="col-span-3">
            <span class="text-xs font-bold uppercase">Antal veckor </span>
            <input type="number" v-model="weeks" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-10">
            <Button label="Spara" class="w-full" @click="saveDateTime()" />
        </div>
    </div>
</template>