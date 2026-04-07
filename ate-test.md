创建一个代理来构建ate-test工作流，创建ate 测试用例，并提交到git仓库。该工作流遵循 Command → Agent → Skill 架构模式：

- 一个命令编排整个流程并处理用户交互

**重要**：所有文件必须创建在 `.claude/` 目录下 。 一切从零构建。Command，Agent，Skill的md文件都用中文来描述。

 设计并实现 `/ate-test` 命令，位于 `.claude/commands/ate-test.md`。该命令执行流程如下：

- 通过命令行工具 git 更新当前仓库

- 添加变动文件到当前仓库中

- push当前仓库到远程git仓库，远程仓库地址为：https://github.com/hexiang1net/ate.git

  
