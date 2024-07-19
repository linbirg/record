<template>
  <div class="shadow">
    <input
      v-if="userId == 1"
      type="text"
      class="add-input"
      autofocus="autofocus"
      placeholder="接下来做什么"
      v-model="content" />
    <div
      class="select-input"
      v-if="userId == 1">
      <el-select
        v-model="owner"
        class="custom-select"
        placeholder="负责人">
        <el-option
          v-for="item in owners"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
      <el-date-picker
        v-model="date"
        type="date"
        class="custom-date"
        placeholder="截止日期">
      </el-date-picker>
      <el-button
        type="text"
        @click="addTodo"
        >提交</el-button
      >
    </div>
    <item
      :todo="todo"
      :userId="userId"
      v-for="todo in filteredTodos"
      :key="todo.todoId"
      @del="deleteTodo"
      @update="updateTodo"></item>
    <tabs
      :filter="filter"
      :todos="todos"
      :userId="userId"
      @toggle="toggleFilter" />
  </div>
</template>

<script>
  import Item from "./item";
  import Tabs from "./tabs";

  export default {
    data() {
      return {
        todos: [
          { todoId: 1, content: "跟踪坤元财务付款流程", owner: "张三", completed: 0, date: "2024-05-22" },
          {
            todoId: 2,
            content: "与梁乘确认交割老oa中pdf文件无法打开问题（暂时通过老系统）",
            owner: "李四",
            completed: 1,
            date: "2024-04-16",
          },
        ],
        owners: [],
        filter: "all",
        content: "",
        owner: "",
        date: "-",
      };
    },
    components: {
      Item,
      Tabs,
    },

    created: function () {
      this.selectAllTodos();
      this.getAllUsers();
    },

    computed: {
      filteredTodos: function () {
        if (this.filter === "all") {
          return this.todos;
        }
        const completed = this.filter === "completed" ? 1 : 0;
        return this.todos.filter((todo) => todo.completed === completed);
      },
      userId: function () {
        return this.$store.state.userId;
      },
    },

    methods: {
      selectAllTodos() {
        this.$store
          .dispatch("get", {
            url: "todo/selectAllTodos.json",
          })
          .then((response) => {
            this.todos = response.todo;
          })
          .catch((err) => {
            console.log(err);
          });
      },
      getAllUsers() {
        let array = [];
        this.$store
          .dispatch("get", {
            // url: 'user/showUser.do?userId=0'
            url: "user/",
          })
          .then((response) => {
            response.forEach((e) => {
              array.push({
                value: e.nickname,
                label: e.nickname,
              });
            });
            this.owners = array;
          })
          .catch((err) => {
            console.log(err);
          });
      },
      addTodo() {
        if (this.content.trim() && this.owner.trim()) {
          let data = {
            content: this.content.trim(),
            owner: this.owner.trim(),
            completed: 0,
            date: this.date,
          };
          this.$store
            .dispatch("post", {
              url: "todo/submitTodo.json",
              data: data,
            })
            .then(() => {
              this.content = "";
              this.owner = "";
              this.date = "-";
              this.selectAllTodos();
            })
            .catch((err) => {
              console.log(err);
            });
        }
      },
      deleteTodo(id) {
        this.$store
          .dispatch("post", {
            url: "todo/deleteTodo.json",
            data: [{ todoId: id }],
          })
          .then(() => {
            this.selectAllTodos();
          })
          .catch((err) => {
            console.log(err);
          });
      },
      updateTodo(obj) {
        this.$store
          .dispatch("post", {
            url: "todo/updateTodo.json",
            data: {
              todoId: obj.todoId,
              completed: obj.completed,
            },
          })
          .then(() => {
            this.selectAllTodos();
          })
          .catch((err) => {
            console.log(err);
          });
      },
      toggleFilter(state) {
        return (this.filter = state);
      },
      // clearAllCompleted() {
      // 	return this.todos = this.todos.filter(todo => todo.completed === false);
      // }
    },
  };
</script>

<style lang="scss" scoped>
  .add-input {
    position: relative;
    margin: 0;
    width: 100%;
    // font-size: 24px;
    font-family: inherit;
    font-weight: inherit;
    line-height: 1.4em;
    border: 0;
    outline: none;
    color: inherit;
    box-sizing: border-box;
    // font-smoothing: antialiased;
    padding: 16px 16px 16px 36px;
    border: none;
    box-shadow: inset 0 -2px 1px rgba(0, 0, 0, 0.03);
  }

  .select-input {
    box-shadow: inset 0 -2px 1px rgba(0, 0, 0, 0.03);
    .el-select,
    .el-input {
      margin: 1px 0;
    }
  }
</style>
<style>
  /* 重置element-ui下的input样式 */
  .custom-select .el-input__inner,
  .custom-date .el-input__inner {
    border-width: 0;
  }
</style>
