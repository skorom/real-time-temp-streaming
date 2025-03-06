using Firebase.Database;
using Firebase.Database.Query;
using Firebase.Database.Streaming;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reactive.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace RealTimeDataVisualization
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private AutoResetEvent renderComplete = new AutoResetEvent(false);

        private List<double> x = new List<double>();
        private List<double> y = new List<double>();

        private FirebaseClient client = new FirebaseClient("https://erts-2025-default-rtdb.europe-west1.firebasedatabase.app/");

        public MainWindow()
        {
            InitializeComponent();
            send.Click += send_Click;
            updateDataDel handler = updateData;

            var child = client.Child("/rpi");

            var observable = child.AsObservable<InboundMessage>();


            var subscription = observable
                .Where(f => !string.IsNullOrEmpty(f.Key))
                .Subscribe(f => updateData(f));
        }

        private void send_Click(object sender, RoutedEventArgs e)
        {
            sendMessage(messageTextBox.Text);
        }

        private async void sendMessage(string message)
        {
            var child = client.Child("message");
            await child.DeleteAsync();
            await child.PostAsync(new OutboundMessage { outMessage = message });
        }
        private delegate void updateDataDel(FirebaseEvent<InboundMessage> f);
        private void updateData(FirebaseEvent<InboundMessage> f)
        {
            if (!Dispatcher.CheckAccess())
                Dispatcher.Invoke(new updateDataDel(updateData), f);
            else
            {
                x.Add(x.Count + 1);
                string tmp = f.Object.temp.Substring(0, 5);
                StringBuilder strb = new StringBuilder(tmp);
                strb[2] = ',';
                y.Add(Convert.ToDouble(strb.ToString()));
                linegraph.Plot(x, y); // x and y are IEnumerable<double>
            }
        }
    }
}
