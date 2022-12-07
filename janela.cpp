#include <gtk/gtk.h>
#include <gst/gst.h>
#include <unistd.h>
#include <stdio.h>
#include <filesystem>
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sys/stat.h>

namespace fs = std::filesystem;

/* Structure to contain all our information, so we can pass it to callbacks */
typedef struct _CustomData {
    GstElement *pipeline;
    GstElement *source;
    GstElement *demuxer;
    GstElement *parser;
    GstElement *decoder;
    GstElement *conv;
    GstElement *sink;
} CustomData;

/* This function will be called by the pad-added signal */
static void pad_added_handler (GstElement *src, GstPad *new_pad, CustomData *data) {
    GstPad *sink_pad = gst_element_get_static_pad (data->parser, "sink");
    GstPadLinkReturn ret;
    GstCaps *new_pad_caps = NULL;
    GstStructure *new_pad_struct = NULL;
    const gchar *new_pad_type = NULL;

    g_print ("Received new pad '%s' from '%s':\n", GST_PAD_NAME (new_pad), GST_ELEMENT_NAME (src));

    /* If our converter is already linked, we have nothing to do here */
    if (gst_pad_is_linked (sink_pad)) {
        g_print ("We are already linked. Ignoring.\n");
        goto exit;
    }

    /* Check the new pad's type */
    new_pad_caps = gst_pad_get_current_caps (new_pad);
    new_pad_struct = gst_caps_get_structure (new_pad_caps, 0);
    new_pad_type = gst_structure_get_name (new_pad_struct);
    g_print ("Recived pad that has type '%s' .\n", new_pad_type);
    if (!g_str_has_prefix (new_pad_type, "video/x-h264")) {
        g_print ("It has type '%s' which is not raw audio. Ignoring.\n", new_pad_type);
        goto exit;
    }

    /* Attempt the link */
    ret = gst_pad_link (new_pad, sink_pad);
    if (GST_PAD_LINK_FAILED (ret)) {
        g_print ("Type is '%s' but link failed.\n", new_pad_type);
    } else {
        g_print ("Link succeeded (type '%s').\n", new_pad_type);
    }

exit:
    /* Unreference the new pad's caps, if we got them */
    if (new_pad_caps != NULL)
        gst_caps_unref (new_pad_caps);

    /* Unreference the sink pad */
    gst_object_unref (sink_pad);
}


void setup_pipeline(CustomData & data) {

    /* Create the elements */
    data.source   = gst_element_factory_make ("filesrc",       "file-source");
    data.demuxer  = gst_element_factory_make ("qtdemux",      "h264-demuxer");
    data.parser   = gst_element_factory_make ("h264parse",      "h264-parser");
    data.decoder  = gst_element_factory_make ("avdec_h264",     "h264-decoder");
    data.conv     = gst_element_factory_make ("videoconvert",  "converter");
    data.sink     = gst_element_factory_make ("autovideosink", "video-output");

    /* Create the empty pipeline */
    data.pipeline = gst_pipeline_new ("video-decoder");

    if (!data.pipeline || !data.source || !data.demuxer || !data.parser || !data.decoder || !data.conv || !data.sink) {
        // one element is not initialized - stop
        g_print("one element is not initialized\n");
        /*
        if (!data.pipeline) {
            g_print("pipe");
        }
        if (!data.source) {
            g_print("src");
        }
        if (!data.demuxer) {
            g_print("dmux");
        }
        if (!data.parser) {
            g_print("parser");
        }
        if (!data.decoder) {
            g_print("decoder");
        }
        if (!data.conv) {
            g_print("conv");
        }
        if (!data.sink) {
            g_print("sink");
        }
        */
        exit(-1);
    }



    /* Build the pipeline. Note that we are NOT linking the source at this
     * point. We will do it later. */
    gst_bin_add_many (GST_BIN (data.pipeline), data.source, data.demuxer, data.parser, data.decoder, data.conv, data.sink, NULL);
    if (gst_element_link_many (data.source, data.demuxer, NULL) != TRUE ||  
            gst_element_link_many(data.parser, data.decoder, data.conv, data.sink, NULL) != TRUE) {
        g_printerr ("Elements could not be linked.\n");
        gst_object_unref (data.pipeline);
        exit(-1);
    }
    /* Connect to the pad-added signal */
    g_signal_connect (data.demuxer, "pad-added", G_CALLBACK (pad_added_handler), &data);

}

void destroy_pipeline(CustomData & data) {
    gst_element_set_state (data.pipeline, GST_STATE_NULL);
    gst_object_unref (data.pipeline);
}

void play_video_mp4(char * filename, CustomData &data) {
    GstStateChangeReturn ret;
    GstBus *bus;
    GstMessage *msg;

    ret = gst_element_set_state (data.pipeline, GST_STATE_READY);
    if (ret == GST_STATE_CHANGE_FAILURE) {
        g_printerr ("Unable to set the pipeline to the paused state.\n");
        gst_object_unref (data.pipeline);
        exit(-1);
    }
    /* Set the URI to play */
    g_object_set (G_OBJECT (data.source), "location", filename, NULL);

    //sleep(2);
    ret = gst_element_set_state (data.pipeline, GST_STATE_PLAYING);
    if (ret == GST_STATE_CHANGE_FAILURE) {
        g_printerr ("Unable to set the pipeline to the paused state.\n");
        gst_object_unref (data.pipeline);
        exit(-1);
    }

    gboolean terminate = FALSE;

    /* Listen to the bus */
    bus = gst_element_get_bus (data.pipeline);
    do {
        msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE,
                (GstMessageType)(GST_MESSAGE_STATE_CHANGED | GST_MESSAGE_ERROR | GST_MESSAGE_EOS));

        /* Parse message */
        if (msg != NULL) {
            GError *err;
            gchar *debug_info;

            switch (GST_MESSAGE_TYPE (msg)) {
                case GST_MESSAGE_ERROR:
                    gst_message_parse_error (msg, &err, &debug_info);
                    g_printerr ("Error received from element %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
                    g_printerr ("Debugging information: %s\n", debug_info ? debug_info : "none");
                    g_clear_error (&err);
                    g_free (debug_info);
                    terminate = TRUE;
                    break;
                case GST_MESSAGE_EOS:
                    g_print ("End-Of-Stream reached.\n");
                    terminate = TRUE;
                    break;
                case GST_MESSAGE_STATE_CHANGED:
                    /* We are only interested in state-changed messages from the pipeline */
                    if (GST_MESSAGE_SRC (msg) == GST_OBJECT (data.pipeline)) {
                        GstState old_state, new_state, pending_state;
                        gst_message_parse_state_changed (msg, &old_state, &new_state, &pending_state);
                        g_print ("Pipeline state changed from %s to %s:\n",
                                gst_element_state_get_name (old_state), gst_element_state_get_name (new_state));
                    }
                    break;
                default:
                    /* We should not reach here */
                    g_printerr ("Unexpected message received.\n");
                    break;
            }
            gst_message_unref (msg);
        }
    } while (!terminate);

    gst_object_unref (bus);
}

extern "C" {
    void sl_insert_button();
    void sl_erase_button();
    void sl_find_button();
    void sl_set_button();

    void sl_element_entry(GtkEntry *e);
    void sl_position_entry(GtkEntry *e);
    void sl_MAX_SIZE_entry(GtkEntry *e);

    void ll_insert_button();
    void ll_erase_button();
    void ll_find_button();
    void ll_set_button();
    void ll_element_entry(GtkEntry *e);
    void ll_position_entry(GtkEntry *e);

    void qu_element_entry(GtkEntry *e);
    void qu_pop_button();
    void qu_push_button();
    void qu_front_button();

    void st_element_entry(GtkEntry *e);
    void st_pop_button();
    void st_push_button();
    void st_top_button();

    void bt_element_entry(GtkEntry *e);
    void bt_insert_button();
    void bt_find_button();
    void bt_in_order_button();

    void notify_stack_switcher(GObject* object, GParamSpec* pspec);

    void windowDelete(GtkWidget *e);
}

typedef
struct {
    FILE * file;
    int part_movie_line;

    char element_buff[256];
    char position_buff[256];
    char MAX_SIZE_buff[256];

    CustomData * data;

    GtkStack * stack;

    GtkEntry * sl_element;
    GtkEntry * sl_position;
    GtkEntry * sl_MAX_SIZE;

    GtkEntry * ll_element;
    GtkEntry * ll_position;

    GtkEntry * qu_element;
    GtkEntry * st_element;

    GtkEntry * bt_element;

} tEnv;

tEnv env = {
    .file = NULL, 
    .part_movie_line = 1,
    .sl_element = NULL,
    .sl_position = NULL,
    .sl_MAX_SIZE = NULL,

    .ll_element = NULL,
    .ll_position = NULL,

    .qu_element = NULL,
    .st_element = NULL,

    .bt_element = NULL,
        };

/* ===== HANDLERS ===== */

void windowDelete(GtkWidget *e) {
    exit(0);
}

void sl_element_entry(GtkEntry *e) {
    strcpy(env.element_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.sl_element = e;
}

void sl_position_entry(GtkEntry *e) {
    strcpy(env.position_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.sl_position = e;
}

void sl_MAX_SIZE_entry(GtkEntry *e) {
    strcpy(env.MAX_SIZE_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.sl_MAX_SIZE = e;
}

// LiskedList
void ll_element_entry(GtkEntry *e) {
    strcpy(env.element_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.ll_element = e;
}

void ll_position_entry(GtkEntry *e) {
    strcpy(env.position_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.ll_position = e;
}

// Queue
void qu_element_entry(GtkEntry *e) {
    strcpy(env.element_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.qu_element = e;
}

// Stack
void st_element_entry(GtkEntry *e) {
    strcpy(env.element_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.st_element = e;
}

// bTree
void bt_element_entry(GtkEntry *e) {
    strcpy(env.element_buff, gtk_entry_get_text(e));
    g_print(gtk_entry_get_text(e));

    env.bt_element = e;
}


/* ===== HANDLERS - End ===== */

#define SCRIPT_NAME "animation"


void file_open_and_append(const char * line) {
    char tmp[256];
    sprintf(tmp, "%s.py", SCRIPT_NAME);
    env.file = fopen(tmp, "ab");

	if(env.file == NULL)
	{
		printf("File not found.\n");
		return;
	}

	//Seek one character from the end of the file.
	fseek(env.file, -1, SEEK_END);

	//Read in a single character;
	char cLastChar = fgetc(env.file);

	if(cLastChar != '\n')
	{
		//Write the line-feed.
		fwrite("\n", sizeof(char), 1, env.file);
	}

    fwrite(line, sizeof(char), strlen(line), env.file);



	//Close the file handle.
	fclose(env.file);
}

void render_and_play(char * class_name) {
    const char *fmt = "manim --fps 60 -ql %s.py %s";
    const char *fmt_file = "media/videos/%s/480p60/partial_movie_files/%s/partial_movie_file_list.txt";
    char tmp[512];
    char tmp2[512];

    sprintf(tmp, fmt, SCRIPT_NAME, class_name);

    if (system(tmp) != 0) {
        g_print("Manim falhou!!?\n");

    }

    sprintf(tmp2, fmt_file, SCRIPT_NAME, class_name);

    std::ifstream infile(tmp2);
    std::string sline;

    std::cout << tmp2 << 
        "\n";

    if (infile.is_open() != true) {
        std::cout << "Abriu n\n";
    }

	for (int i = 0; std::getline(infile, sline); i++) {
        if (i >= env.part_movie_line) {
            // pegar nome do arquivo
            char buff[256];
            sscanf(sline.c_str(), "file \'file:%[^\'\n]", buff);

            play_video_mp4(buff, *env.data);

            puts(buff);
            env.part_movie_line = i+1;
        }
    }
}

void clear_entries() {
    if (env.sl_element) {
        gtk_entry_set_text(GTK_ENTRY(env.sl_element), "");
    }

    if (env.sl_position) {
        gtk_entry_set_text(GTK_ENTRY(env.sl_position), "");
    }

    // LinkedList
    if (env.ll_element) {
        gtk_entry_set_text(GTK_ENTRY(env.ll_element), "");
    }

    if (env.ll_position) {
        gtk_entry_set_text(GTK_ENTRY(env.ll_position), "");
    }

    // queue
    if (env.qu_element) {
        gtk_entry_set_text(GTK_ENTRY(env.qu_element), "");
    }
    // stack
    if (env.st_element) {
        gtk_entry_set_text(GTK_ENTRY(env.st_element), "");
    }

    // tree
    if (env.bt_element) {
        gtk_entry_set_text(GTK_ENTRY(env.bt_element), "");
    }


}

#define FMT_INSERT_DBL  "        self.insert(%d, %d)\n"
#define FMT_INSERT      "        self.insert(%d)\n"
#define FMT_ERASE       "        self.erase(%d)\n"
#define FMT_SEARCH      "        self.search(%d)\n"
#define FMT_RESIZE      "        self.resize(%d)\n"

#define FMT_FRONT       "        self.front()\n"
#define FMT_TOP         "        self.top()\n"

#define FMT_POP         "        self.pop()\n"
#define FMT_PUSH        "        self.push(%d)\n"

#define FMT_IN_ORDER    "        self.in_order()\n"

#define FMT_SCRIPT_DIR  "scripts/%s.py"

#define LLIST "LinkedList"
#define SLIST "ListSeq"
#define QUEUE "Queue"
#define STACK "Stack"
#define BTREE "BinarySearchTree"


void sl_insert_button() {
    g_print("Insert Clicked\n");

    char tmp[256];
    int element = atoi(env.element_buff);
    int pos = atoi(env.position_buff);

    sprintf(tmp, FMT_INSERT_DBL, pos, element);
    g_print(tmp);

    // add nova linha referente a nova animacao
    file_open_and_append(tmp);

    render_and_play(SLIST);

    clear_entries();
}

void sl_erase_button() {
    g_print("Erase Clicked\n");

    char tmp[256];
    int pos = atoi(env.position_buff);

    sprintf(tmp, FMT_ERASE, pos);
    g_print(tmp);

    file_open_and_append(tmp);

    render_and_play(SLIST);

    clear_entries();

}

void sl_find_button() {
    g_print("search Clicked\n");

    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_SEARCH, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(SLIST);

    clear_entries();
}

void sl_set_button() {
    g_print("set Clicked\n");

    char tmp[256];
    int size = atoi(env.MAX_SIZE_buff);

    sprintf(tmp, FMT_RESIZE, size);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(SLIST);

    clear_entries();
}

// LinkedList
void ll_insert_button() {
    g_print("Insert Clicked\n");

    char tmp[256];
    int element = atoi(env.element_buff);
    int pos = atoi(env.position_buff);

    sprintf(tmp, FMT_INSERT_DBL, pos, element);
    g_print(tmp);

    // add nova linha referente a nova animacao
    file_open_and_append(tmp);

    render_and_play(LLIST);

    clear_entries();
}

void ll_erase_button() {
    g_print("Erase Clicked\n");

    char tmp[256];
    int pos = atoi(env.position_buff);

    sprintf(tmp, FMT_ERASE, pos);
    g_print(tmp);

    file_open_and_append(tmp);

    render_and_play(LLIST);

    clear_entries();

}

void ll_find_button() {
    g_print("search Clicked\n");

    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_SEARCH, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(LLIST);

    clear_entries();
}

// Queue
void qu_push_button() {
    g_print("push Clicked\n");

    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_PUSH, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(QUEUE);

    clear_entries();
}


void qu_pop_button() {
    g_print("pop Clicked\n");


    g_print(FMT_POP);

    file_open_and_append(FMT_POP);

    
    render_and_play(QUEUE);

    clear_entries();
}


void qu_front_button() {
    g_print("pop Clicked\n");


    g_print(FMT_FRONT);

    file_open_and_append(FMT_FRONT);

    
    render_and_play(QUEUE);

    clear_entries();
}


// Stack
void st_push_button() {
    g_print("push Clicked\n");

    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_PUSH, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(STACK);

    clear_entries();
}


void st_pop_button() {
    g_print("pop Clicked\n");


    g_print(FMT_POP);

    file_open_and_append(FMT_POP);

    
    render_and_play(STACK);

    clear_entries();
}


void st_top_button() {
    g_print("pop Clicked\n");


    g_print(FMT_FRONT);

    file_open_and_append(FMT_TOP);

    
    render_and_play(STACK);

    clear_entries();
}

// Stack
void bt_insert_button() {
    g_print("push Clicked\n");

    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_INSERT, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(BTREE);

    clear_entries();
}


void bt_find_button() {
    g_print("pop Clicked\n");


    char tmp[256];
    int e = atoi(env.element_buff);

    sprintf(tmp, FMT_SEARCH, e);
    g_print(tmp);

    file_open_and_append(tmp);

    
    render_and_play(BTREE);

    clear_entries();
}


void bt_in_order_button() {
    g_print("pop Clicked\n");


    file_open_and_append(FMT_IN_ORDER);

    
    render_and_play(BTREE);

    clear_entries();
}


void notify_stack_switcher(GObject* object, GParamSpec* pspec) {
    g_print("mudou!\n");

    auto page_name = gtk_stack_get_visible_child_name(env.stack);

    printf("%s\n", page_name);

    destroy_pipeline(*env.data);
    setup_pipeline(*env.data);

    env.part_movie_line = 1;

    char tmp[256];
    char cmd[512];

    if (g_strcmp0(page_name, "list_seq") == 0) {
        sprintf(tmp, FMT_SCRIPT_DIR, SLIST);
    } else if (g_strcmp0(page_name, "list_linked") == 0){
        sprintf(tmp, FMT_SCRIPT_DIR, LLIST);
    } else if (g_strcmp0(page_name, "queue") == 0){
        sprintf(tmp, FMT_SCRIPT_DIR, QUEUE);
    } else if (g_strcmp0(page_name, "b-tree") == 0){
        sprintf(tmp, FMT_SCRIPT_DIR, BTREE);
    } else if (g_strcmp0(page_name, "stack") == 0){
        sprintf(tmp, FMT_SCRIPT_DIR, STACK);
    }

    sprintf(cmd, "cp %s %s.py", tmp, SCRIPT_NAME);
    system(cmd);

}

int main(int argc, char *argv[]) {
    CustomData data;
    env.data = &data;

    gst_init (&argc, &argv);

    setup_pipeline(data);

    char tmp[256];
    char cmd[512];
    sprintf(tmp, FMT_SCRIPT_DIR, SLIST);
    sprintf(cmd, "cp %s %s.py", tmp, SCRIPT_NAME);
    system(cmd);




    GtkWidget *window;
    GtkBuilder *builder = NULL;

    gtk_init (&argc , &argv);

    builder = gtk_builder_new();

    if( gtk_builder_add_from_file (builder,"janela-gtk/janela.glade" , NULL) == 0) {
        printf("gtk_builder_add_from_file FAILED\n");
        return(0);
    }

    window  = GTK_WIDGET (gtk_builder_get_object (builder,"window"));

    env.stack  = GTK_STACK (gtk_builder_get_object (builder,"st1"));
    /*
    GValue box_seq_title = G_VALUE_INIT;
    g_value_init (&box_seq_title, G_TYPE_STRING);
    g_value_set_string(&box_seq_title, "ListaSeq");

    auto box_seq  = GTK_BOX (gtk_builder_get_object (builder,"box-seq"));

    gtk_container_child_set_property(GTK_CONTAINER(stack), GTK_WIDGET(box_seq), "title", &box_seq_title);
    */
  

    gtk_builder_connect_signals(builder,NULL);

    gtk_widget_show_all (window);
    gtk_main ();




    destroy_pipeline(data);
    return 0;
}

/*
gboolean windowDelete(__attribute__((unused)) GtkWidget *widget, 
                      __attribute__((unused)) GdkEvent  *event,
                      __attribute__((unused)) gpointer   data)
{
    g_print("%s called.\n",__FUNCTION__);
    return TRUE;    // Returning TRUE stops the window being deleted.
                    // Returning FALSE allows deletion.   
}
*/


