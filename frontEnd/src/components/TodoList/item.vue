<template>
  <div :class="['todo-item', todo.completed ? 'completed': '']">
      <input 
        type="checkbox"
        class="toggle"
        v-model="todo.completed"
				@click="updateTodo"
				v-if="userId == 1"
      >
			<label class="line-1">{{todo.content}}</label>
			<label class="line-2">责任人：{{todo.owner}}; 计划完成时间：{{todo.date.slice(0, 10)}}</label>
			<span class="destroy" @click="deleteTodo" v-if="userId == 1"><i class="el-icon-close"></i></span>
  </div>
</template>

<script>
	export default {
		props: {
			todo: {
				type: Object,
				required: true,
			},
			userId: {
				required: true
			}
		},
		methods: {
			deleteTodo() {
				this.$emit('del', this.todo.todoId)
			},
			updateTodo() {
				this.$emit('update', {todoId: this.todo.todoId, completed: !this.todo.completed === true ? 1 : 0})
			}
		}
	}
</script>

<style lang="scss" scoped>
.todo-item {
	position: relative;
	background-color: #fff;
	border-bottom: 1px solid rgba(0,0,0,0.06);
	.el-icon-close{
		display: none;
	}
	&:hover {
		.destroy .el-icon-close{
			display: inline;
		}
	}
	label{
		white-space: pre-line;
		word-break: break-all;
		
		margin-left: 45px;
		display: block;
		line-height: 1.2;
		transition: color 0.4s;
	}
	.line-1 {
		padding: 15px 60px 1px 15px;
	}
	.line-2 {
		padding: 1px 60px 15px 15px;
		color: #949494;
	}
	&.completed{
		label{
			color: #d9d9d9;
			text-decoration: line-through;
		}
	}
}
.toggle{
	text-align: center;
	width: 40px;
	height: 40px;
	line-height: 40px;
	position: absolute;
	top: 0;
	bottom: 0;
	margin: auto 0;
	border: none;
	appearance: none;
	outline: none;
	padding-left: 5px;
	cursor: pointer;
	&:after{
		content: url('../../assets/images/round.svg');
	}
	&:checked:after{
		content: url('../../assets/images/done.svg');
	}
}
.destroy{
	position: absolute;
	top: 0;
	right: 10px;
	bottom: 0;
	width: 40px;
	height: 40px;
	margin: auto 0;
	font-size: 24px;
	color: #cc9a9a;
	// margin-bottom: 11px;
	transition: color 0.2s ease-out;
	background-color: transparent;
	appearance: none;
	border-width: 0;
	cursor: pointer;
	outline: none;
}
</style>

