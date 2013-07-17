#include "glpropertyeditor.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    GLPropertyEditor w;
    w.show();
    
    return a.exec();
}
