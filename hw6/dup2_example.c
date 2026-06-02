#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

int main() {
    int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open 失敗");
        return 1;
    }

    printf("這行會印在螢幕上\n");

    // dup2：把 fd 複製到 stdout (1)
    // 效果：所有寫到 stdout 的內容跑去檔案
    dup2(fd, STDOUT_FILENO);

    printf("這行會寫入 output.txt 而不是螢幕\n");
    write(STDOUT_FILENO, "這也是寫入檔案\n", strlen("這也是寫入檔案\n"));

    close(fd);
    return 0;
}
