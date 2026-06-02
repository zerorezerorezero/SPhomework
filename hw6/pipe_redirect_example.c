#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <string.h>

int main() {
    int pipefd[2];
    pipe(pipefd);  // pipefd[0] = 讀端, pipefd[1] = 寫端

    pid_t pid = fork();

    if (pid == 0) {
        // === 子行程：把 ls 的輸出抓到 pipe ===
        close(pipefd[0]);                // 關掉讀端（不需要）

        dup2(pipefd[1], STDOUT_FILENO);  // stdout → pipe 寫端
        close(pipefd[1]);                // 關掉原本的 fd

        execlp("ls", "ls", "-l", NULL);  // ls 的輸出全部進 pipe
        perror("execlp 失敗");
        return 1;
    }

    // === 父行程：從 pipe 讀取 ls 的輸出 ===
    close(pipefd[1]);  // 關掉寫端（不需要）

    char buffer[4096];
    ssize_t n = read(pipefd[0], buffer, sizeof(buffer) - 1);
    close(pipefd[0]);

    wait(NULL);

    if (n > 0) {
        buffer[n] = '\0';
        printf("從 pipe 收到 ls 的輸出：\n%s\n", buffer);
    }

    return 0;
}
