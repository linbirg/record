<template>
  <!-- <section class="real-app" v-if="typeId < 2"> -->
  <section class="real-app">
    <!-- <Todo></Todo> -->
    <!-- <Calendar></Calendar> -->
  </section>
</template>
<script>
import Todo from './TodoList/todo'
import Calendar from './Calendar/calendar'
// import WeekReport from './Calendar/weekreport'
export default {
  components: {
    Todo,
    Calendar,
    // WeekReport
  },
  computed: {
    typeId() {
      return this.$store.state.typeId
    }
  }
}
</script>
<style lang="scss" scoped>
.real-app {
	position: fixed;
	top: 72px;
	left: 1135px;
	width: 500px;
	margin: 0 auto;
	font-size: 14px;
	
}
.shadow{
  margin-bottom: 5px;
  border: 1px solid #ebeef5;
	box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
	background-color: #fff;
}
</style>