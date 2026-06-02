#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();

    if (pid == 0) {
        // 子行程：用 execvp 執行 ls 指令
        printf("子行程準備執行 ls...\n\n");

        char *args[] = {"ls", "-l", NULL};
        execvp("ls", args);

        // 如果 execvp 成功，以下不會執行
        perror("execvp 失敗");
        return 1;
    }

    // 父行程：等小孩
    wait(NULL);
    printf("\n父行程：子行程執行完畢\n");

    return 0;
}
