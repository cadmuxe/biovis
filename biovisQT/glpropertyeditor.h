#ifndef GLPROPERTYEDITOR_H
#define GLPROPERTYEDITOR_H

#include <QDialog>

namespace Ui {
class GLPropertyEditor;
}

class GLPropertyEditor : public QDialog
{
    Q_OBJECT
    
public:
    explicit GLPropertyEditor(QWidget *parent = 0);
    ~GLPropertyEditor();
    
private:
    Ui::GLPropertyEditor *ui;
};

#endif // GLPROPERTYEDITOR_H
