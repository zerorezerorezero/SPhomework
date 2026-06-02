#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失敗");
        return 1;
    }

    if (pid == 0) {
        // === 子行程 ===
        printf("我是子行程，我的 PID = %d\n", getpid());
        printf("我的爸爸 PID = %d\n", getppid());
    } else {
        // === 父行程 ===
        printf("我是父行程，我的 PID = %d\n", getpid());
        printf("我生的子行程 PID = %d\n", pid);

        int status;
        wait(&status);  // 等子行程結束，避免殭屍行程
        printf("子行程結束了\n");
    }

    return 0;
}
