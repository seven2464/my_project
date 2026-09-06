#定义了一个名为 delete_files() 的函数，它接受一个目录路径作为参数。
#函数首先使用 os.listdir() 函数获取目录中的文件列表。然后，我们使用一个循环遍历该列表，并使用 os.remove() 函数删除每个文件。
import os

def delete_files(directory):
    file_list = os.listdir(directory)
    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# 调用示例
directory_path = r'photo/Original'
delete_files(directory_path)

def delete_file(directory):
    file_list = os.listdir(directory)
    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# 调用示例
directory_path = r'photo/Tag'
delete_file(directory_path)
