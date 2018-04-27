#!C:\myApplications\Perl\Strawberry\perl\bin\perl -sw
#!/usr/bin/perl -sw
my $version = "1.00";

# Created by Steve Voisey (srv) 15 Feb 2018.
# email: [stevevoisey@yahoo.com]
# 

# --outputtv 
#    get_iplayer --prefs-add --subdir --outputradio="/iplayer/radio/current"  --radiomode="hafstd,hafmed,vgood"
#    get_iplayer --prefs-add --subdir --outputtv="/iplayer/television/current"
#    get_iplayer --prefs-add --output="/iplayer/radio/current"
#    get_iplayer --prefs-add --no-purge
#
#    [root@nas01 iplayer]# get_iplayer --prefs-show
# Options in '/root/.get_iplayer/options'
#         radiomode = hafstd,hafmed,vgood
#         ffmpeg = /usr/local/bin/ffmpeg
#         outputtv = /iplayer/television/current
#        nopurge = 1
#        output = /iplayer/radio/current
#        outputradio = /iplayer/radio/current
#        subdir = 1

###my $radio = "radio.list";

use Cwd;

my $divide = "=" x 80 . "\n";
#$dateTimeStamp = `date "+%Y%m%d_%H%M"`;
my $dateTimeStamp = "today";
chomp($dateTimeStamp);


#my $properties{thisDir} = cwd();
#chomp($properties{thisDir});

my $thisDir = cwd();
chomp($thisDir);

unless(defined($environment)) { if ($^O =~ /MSWin32/) { $environment = "windows"; } else { $environment = "linux";} }

#unless(defined($home))       { $home = "/iplayer"; }

if ( $environment =~ /windows/i ) { 
    unless(defined($code_home))  { $code_home = "C:/git/iplayer-code"; }
    unless(defined($data_home))  { $data_home = "C:/iplayer"; }
    $playCommand = "get_iplayer.pl"
} else { 
    $home = "/iplayer"; 
    $share = "/iplayer"; 
    $playCommand = "get_iplayer"
}

  
unless(defined($winshare))   { $winshare = "C:/iplayer"; }
unless(defined($share))      { $share = $winshare; }

unless(defined($scripts))    { $scripts = "$code_home/scripts"; }
unless(defined($conf))       { $conf    = "$code_home/config"; }
unless(defined($logFile))    { $logFile = "$data_home/logs/autoGetIplayer_${dateTimeStamp}.log"; }
unless(defined($scriptFile))    { $scriptFile = "$data_home/batch_autoGetIplayer.bat"; }
unless(defined($options))    { $options = ""; }

###$force = "true";
if(defined($force))          { $options = "--force --overwrite --tvmode=best"; }
if(defined($force))          { $options = "--force --overwrite"; }
if(defined($force))          { $x=1; }

if(defined($tv))             { unless(defined($television)) { $television = $tv; }}

$standardOptions = "--subdir --nopurge";
$voiceOptions    = "--type=radio --outputradio=${share}/radio/current ${standardOptions}";
#$musicOptions    = "--type=radio --outputradio=${share}/music/current -radiomode=\"hafstd,hafmed,vgood\" ${standardOptions}";
$musicOptions    = "--type=radio --outputradio=${share}/music/current -radiomode=best ${standardOptions}";
$tvOptions       = "--type=tv --outputtv=${share}/television/current ${standardOptions}";



@television = ();
@radio      = ();
@music      = ();

#print "radio: $radio\n";

#Y:\iplayer\radio

print "hello: $logFile\n";

unless (open (OUT, ">$logFile"))   { die "cannot open output file $logFile $!"; }
unless (open (SCR, ">$scriptFile"))   { die "cannot open output file $scriptFile $!"; }

print SCR "setx IPLAY_DIR 'C:\\Program Files (x86)\\get_iplayer'\n";
print SCR "setx PERL_DIR 'C:\\Program Files (x86)\\get_iplayer\\perl'\n";

if(defined($radio)) { 
    print "radio file: $conf/$radio\n";
    if( -f "$conf/$radio" ) 
        { unless (open (RADIO, "<$conf/$radio"))   { die "cannot open input file $conf/$radio $!"; }}
    else 
        { print "not a file? $conf/$radio\n"; }
        
    @radio = <RADIO>;
    close RADIO;
}

if(defined($television) || defined($tv)) { 
    print "television file: $conf/$television\n";
    if( -f "$conf/$television" ) { unless (open (TV, "<$conf/$television"))   { die "cannot open input file $conf/$television $!"; }}
    @tv = <TV>;
    close TV;
}

if(defined($music)) {
    print "music file: $conf/$music\n";
 
    if( -f "$conf/$music" ) { unless (open (MUSIC, "<$conf/$music"))   { die "cannot open input file $conf/$music $!"; }}
    @music = <MUSIC>;
    close MUSIC;
}

if ( @radio > 0 ) { process(\@radio, "radio"); }
if ( @tv > 0 )    { process(\@tv, "television"); }
if ( @music > 0 ) { process(\@music, "music"); }

exit;

###################################################################################
#  subroutine: process
###################################################################################

sub process {
    my $array_ref = $_[0];
    my $type      = $_[1];
    unless(defined($type)) { $type = "radio"; }
    
    $count = 0;
    foreach $line (@$array_ref) {
        $count++;
        $command = "NONE";
        ( $option, $program ) = "";
        chomp($line);
        $line =~ s/\R\z//;

        if ( $line =~ /^END-NOW$/ ) { last; }
        if ( $line =~ /^\s*$/ ) { next; }
        if ( $line =~ /^#/ )    { next; }
        if ( $line =~ /\|/ )    { 
            ( $program, $option ) = $line =~ /^(.*)\|(.*)$/;
        } else {
            $program = $line;
        }
        if ( $option =~ /series/ ) { $series = "--pid-recursive"; } else { $series = ""; }
        
        print "line: $line\nprogram: [$program] option: [$option] series: [$series]\n";
        
        
        if ( $program =~ /^["'].*["']\s*$/ ) {
            if ( $type =~ /radio/i ) {
                $command = "$playCommand $voiceOptions ${program} ${options} --get ";
            }
            if ( $type =~ /television/i ) {
                $command = "$playCommand $tvOptions ${program} ${options} --get ";
            }
            if ( $type =~ /music/i ) {
                $command = "$playCommand $musicOptions ${program} ${options} --get";
            }
        }

        if ( $program =~ /^[\d\w]+$/ ) {
            if ( $type =~ /radio/i ) {
                $command = "$playCommand $voiceOptions --pid=${program} $series --get ${options}";
            }
            if ( $type =~ /television/i ) {
                $command = "$playCommand $tvOptions --pid=${program} $series --get ${options}";
            }
            if ( $type =~ /music/i ) {
                $command = "$playCommand $musicOptions --pid=${program} $series --get ${options}";
            }
        }           

        unless ( $command =~ /NONE/ ) {
            print "command: $command\n";
            $out = `$command`;
            #system($command);
            print "out: $out\n";
            print OUT "$command\n$out\n";
            ##perl.exe  "%IPLAY_DIR%"/get_iplayer.pl
            ##print OUT "$command\n";
            print SCR "perl.exe  \"%IPLAY_DIR%\"/$command\n";
        }
    }
}

close OUT;
close SCR;
