<script setup>
    import {ref, inject} from 'vue'
   
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['onAddedResources'])

    const resources = ref(dialogRef.value.data.resources)
    const resource_name = ref()

    const addResource = function(){
        resources.value.push(
            {
                name: resource_name.value
            }
        )
        resource_name.value = ''
        console.log('We are emitting', resources)
        emit('AddedResources', resources)
    }
</script>
<template>
    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-9">
            <span class="text-xs font-bold uppercase">Namn </span><small class="text-xs font-light">t.ex Daniel</small>
            <input type="text" v-model="resource_name" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-1">
            <span class="text-xs font-bold uppercase">&nbsp;</span><br />
            <Button label="+" class="w-full float-right" style="height:42px" @click="addResource()" />
        </div>
        <div class="col-span-10">
            <span class="text-xs font-bold uppercase">Resurser </span>
            <DataTable :value="resources" class="p-datatable-sm" scrollable scrollHeight="200px">
                <Column field="name" header="Resurs"></Column>
            </DataTable>
        </div>
    </div>
</template>